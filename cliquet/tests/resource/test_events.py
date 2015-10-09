from cliquet.tests.resource import BaseTest


class ResourceEventTest(BaseTest):
    def test_create_event_is_sent_on_post(self):
        # Simulate incoming POST request on collection.
        self.resource.request.validated = {'data': {'title': 'Coucou'}}
        self.resource.collection_post()
        # Verify that notify() method of request was called with event.
        last_call = self.resource.request.notify.call_args[0]
        event_name, payload = last_call
        self.assertEqual(event_name, 'Created')
        self.assertEqual(payload['title'], 'Coucou')
        self.assertIn('id', payload)
        self.assertIn('last_modified', payload)
