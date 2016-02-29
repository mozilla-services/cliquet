# -*- coding: utf-8 -*-
import json
import uuid
from contextlib import contextmanager
from datetime import datetime
import time

import mock
from pyramid import testing

from cliquet import initialization
from cliquet.events import ResourceChanged, ResourceRead, ACTIONS
from cliquet.listeners import ListenerBase
from cliquet.storage.redis import create_from_config
from cliquet.tests.support import unittest, DummyRequest, BaseWebTest


class ListenerSetupTest(unittest.TestCase):
    def setUp(self):
        redis_patch = mock.patch('cliquet.listeners.redis.load_from_config')
        self.addCleanup(redis_patch.stop)
        self.redis_mocked = redis_patch.start()

    def make_app(self, extra_settings={}):
        settings = {
            'event_listeners': 'cliquet.listeners.redis',
        }
        settings.update(**extra_settings)
        config = testing.setUp(settings=settings)
        config.commit()
        initialization.setup_listeners(config)
        return config

    def test_listener_module_is_specified_via_settings(self):
        self.make_app({
            'event_listeners': 'redis',
            'event_listeners.redis.use': 'cliquet.listeners.redis',
        })
        self.assertTrue(self.redis_mocked.called)

    def test_listener_module_can_be_specified_via_listeners_list(self):
        self.make_app()
        self.assertTrue(self.redis_mocked.called)

    def test_callback_called_when_action_is_not_filtered(self):
        config = self.make_app()
        event = ResourceChanged(ACTIONS.CREATE, 123456, [], DummyRequest())
        config.registry.notify(event)

        self.assertTrue(self.redis_mocked.return_value.called)

    def test_callback_is_not_called_when_action_is_filtered(self):
        config = self.make_app({
            'event_listeners.redis.actions': 'delete',
        })
        event = ResourceChanged(ACTIONS.CREATE, 123456, [], DummyRequest())
        config.registry.notify(event)

        self.assertFalse(self.redis_mocked.return_value.called)

    def test_callback_called_when_resource_is_not_filtered(self):
        config = self.make_app()
        event = ResourceChanged(ACTIONS.CREATE, 123456, [], DummyRequest())
        event.payload['resource_name'] = 'mushroom'
        config.registry.notify(event)

        self.assertTrue(self.redis_mocked.return_value.called)

    def test_callback_is_not_called_when_resource_is_filtered(self):
        config = self.make_app({
            'event_listeners.redis.resources': 'toad',
        })
        event = ResourceChanged(ACTIONS.CREATE, 123456, [], DummyRequest())
        event.payload['resource_name'] = 'mushroom'
        config.registry.notify(event)

        self.assertFalse(self.redis_mocked.return_value.called)

    def test_callback_is_not_called_on_read_by_default(self):
        config = self.make_app()
        event = ResourceRead(ACTIONS.READ, 123456, [], DummyRequest())
        config.registry.notify(event)

        self.assertFalse(self.redis_mocked.return_value.called)

    def test_callback_is_called_on_read_if_specified(self):
        config = self.make_app({
            'event_listeners.redis.actions': 'read',
        })
        event = ResourceRead(ACTIONS.READ, 123456, [], DummyRequest())
        config.registry.notify(event)

        self.assertTrue(self.redis_mocked.return_value.called)

    def test_same_callback_is_called_for_read_and_write_specified(self):
        config = self.make_app({
            'event_listeners.redis.actions': 'read create delete',
        })
        event = ResourceRead(ACTIONS.READ, 123456, [], DummyRequest())
        config.registry.notify(event)
        event = ResourceChanged(ACTIONS.CREATE, 123456, [], DummyRequest())
        config.registry.notify(event)

        self.assertEqual(self.redis_mocked.return_value.call_count, 2)


@contextmanager
def broken_redis():
    from redis import StrictRedis
    old = StrictRedis.lpush

    def push(*args, **kwargs):
        raise Exception('boom')

    StrictRedis.lpush = push
    yield
    StrictRedis.lpush = old


class ListenerCalledTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.add_settings({
            'event_listeners': 'redis',
            'event_listeners.redis.use': 'cliquet.listeners.redis',
            'event_listeners.redis.pool_size': '1',
            'events_pool_size': 1,
            'events_url': 'redis://localhost:6379/0'})
        initialization.setup_listeners(self.config)
        self.config.commit()
        self._redis = create_from_config(self.config, prefix='events_')
        self._size = 0

    def _save_redis(self):
        self._size = self._redis.llen('cliquet.events')

    def has_redis_changed(self):
        return self._redis.llen('cliquet.events') > self._size

    def notify(self, event):
        self._save_redis()
        self.config.registry.notify(event)

    def test_redis_is_notified(self):
        # let's trigger an event
        event = ResourceChanged(ACTIONS.CREATE, 123456, [], DummyRequest())
        self.notify(event)
        self.assertTrue(self.has_redis_changed())

        # okay, we should have the first event in Redis
        last = self._redis.lpop('cliquet.events')
        last = json.loads(last.decode('utf8'))
        self.assertEqual(last['action'], ACTIONS.CREATE.value)

    def test_notification_is_broken(self):
        # an event with a bad JSON should silently break and send nothing
        # date time objects cannot be dumped
        event2 = ResourceChanged(ACTIONS.CREATE,
                                 datetime.now(),
                                 [],
                                 DummyRequest())
        self.notify(event2)
        self.assertFalse(self.has_redis_changed())

    def test_redis_is_broken(self):
        # if the redis call fails, same deal: we should ignore it
        self._save_redis()

        with broken_redis():
            event = ResourceChanged(ACTIONS.CREATE, 123456, [], DummyRequest())
            self.config.registry.notify(event)

        self.assertFalse(self.has_redis_changed())


class AsyncListenerCalledTest(BaseWebTest, unittest.TestCase):

    def get_app_settings(self, extra=None):
        settings = super(AsyncListenerCalledTest, self).get_app_settings(extra)
        settings.update({
            'event_listeners': 'redis',
            'event_listeners.redis.use': 'cliquet.listeners.redis',
            'event_listeners.redis.pool_size': '1',
            'event_listeners.redis.async': 'true',
            'background.workers': 'cliquet.workers.memory',
            'events_pool_size': 1,
            'events_url': 'redis://localhost:6379/0'})
        return settings

    def test_relies_on_workers_if_listener_is_async(self):
        with mock.patch.object(self.workers, 'apply_async') as mocked:
            self.app.post_json('/mushrooms',
                               {'data': {'name': 'blanc'}},
                               headers=self.headers)
            self.assertTrue(mocked.called)

    def test_calls_listener_asynchronously(self):
        self.app.post_json('/mushrooms',
                           {'data': {'name': 'blanc'}},
                           headers=self.headers)
        tasks = self.workers.in_progress('event')
        self.assertEqual(len(tasks), 1)


class ListenerBaseTest(unittest.TestCase):

    def test_not_implemented(self):
        # make sure we can't use the base listener
        listener = ListenerBase()
        self.assertRaises(NotImplementedError, listener, object())

    def test_done_logs_by_default(self):
        listener = ListenerBase()
        with mock.patch('cliquet.logger.info') as mocked:
            listener.done(name='event', res_id=123, success=True, result=None)
            self.assertTrue(mocked.called)
