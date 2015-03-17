import mock
from .support import BaseWebTest, unittest


MINIMALIST_ARTICLE = dict(title="MoFo",
                          url="http://mozilla.org",
                          added_by="FxOS")


class IntegrationTest(BaseWebTest, unittest.TestCase):
    def test_all_views_does_not_accept_basic_auth_when_deactivated(self):
        with mock.patch.dict(
                self.app.app.registry.settings,
                [('cliquet.basic_auth_enabled', False)]):

            headers = {'Authorization': 'Basic YWJjOmFi',
                       'Content-Type': 'application/json'}
            self.app.get('/articles', status=401, headers=headers)
            self.app.post_json('/articles', MINIMALIST_ARTICLE, status=401,
                               headers=headers)

            url = '/articles/:id'
            self.app.get(url, status=401, headers=headers)
            self.app.patch_json(url, MINIMALIST_ARTICLE, status=401,
                                headers=headers)
            self.app.delete(url, status=401, headers=headers)

    def test_replacing_records_is_not_allowed_even_logged_out(self):
        resp = self.app.put_json('/articles/:id',
                                 MINIMALIST_ARTICLE,
                                 headers=self.headers,
                                 status=405)
        self.assertEqual(resp.json['errno'], 115)

    def test_options_on_articles_works(self):
        self.app.options(
            '/articles',
            headers={'Access-Control-Request-Method': 'GET',
                     'Origin': 'http://localhost/'},
            status=200)


class ArticleModificationTest(BaseWebTest, unittest.TestCase):
    def setUp(self):
        super(ArticleModificationTest, self).setUp()
        resp = self.app.post_json('/articles',
                                  MINIMALIST_ARTICLE,
                                  headers=self.headers)
        self.before = resp.json
        self.url = '/articles/{id}'.format(id=self.before['id'])

    def test_replacing_records_is_not_allowed(self):
        resp = self.app.put_json(self.url,
                                 MINIMALIST_ARTICLE,
                                 headers=self.headers,
                                 status=405)
        self.assertEqual(resp.json['errno'], 115)

    def test_resolved_url_and_titles_are_set(self):
        self.assertEqual(self.before['resolved_url'], "http://mozilla.org")
        self.assertEqual(self.before['resolved_title'], "MoFo")

    def test_resolved_url_and_titles_can_be_modified(self):
        body = {
            'resolved_url': 'https://ssl.mozilla.org',
            'resolved_title': 'MoFo secure'
        }
        updated = self.app.patch_json(self.url, body, headers=self.headers)
        self.assertNotEqual(self.before['resolved_url'],
                            updated.json['resolved_url'])
        self.assertNotEqual(self.before['resolved_title'],
                            updated.json['resolved_title'])

    def test_cannot_modify_url(self):
        body = {'url': 'http://immutable.org'}
        self.app.patch_json(self.url,
                            body,
                            headers=self.headers,
                            status=400)

    def test_cannot_modify_stored_on(self):
        body = {'stored_on': 1234}
        self.app.patch_json(self.url,
                            body,
                            headers=self.headers,
                            status=400)

    def test_cannot_mark_as_read_without_by_and_on(self):
        body = {'unread': False}
        resp = self.app.patch_json(self.url,
                                   body,
                                   headers=self.headers,
                                   status=400)
        self.assertIn('Missing marked_read_by', resp.json['message'])


class ReadArticleModificationTest(BaseWebTest, unittest.TestCase):
    def setUp(self):
        super(ReadArticleModificationTest, self).setUp()

        resp = self.app.post_json('/articles',
                                  MINIMALIST_ARTICLE,
                                  headers=self.headers)
        before = resp.json
        self.url = '/articles/{id}'.format(id=before['id'])

        mark_read = {
            'read_position': 42,
            'unread': False,
            'marked_read_by': 'FxOS',
            'marked_read_on': 1234}
        resp = self.app.patch_json(self.url, mark_read, headers=self.headers)
        self.record = resp.json

    def refetch(self):
        resp = self.app.get(self.url, headers=self.headers)
        return resp.json

    def test_patch_changes_are_taken_into_account(self):
        record = self.refetch()
        self.assertEqual(record['marked_read_by'], 'FxOS')
        self.assertEqual(record['marked_read_on'], 1234)
        self.assertEqual(record['read_position'], 42)

    def test_mark_by_and_on_are_set_to_none_if_unread_is_true(self):
        self.app.patch_json(self.url,
                            {'unread': True},
                            headers=self.headers)
        record = self.refetch()
        self.assertIsNone(record['marked_read_by'])
        self.assertIsNone(record['marked_read_on'])

    def test_read_position_is_reset_when_unread_is_set_to_true(self):
        self.app.patch_json(self.url,
                            {'unread': True},
                            headers=self.headers)
        record = self.refetch()
        self.assertEqual(record['read_position'], 0)

    def test_read_position_is_ignored_if_set_to_lower_value(self):
        self.app.patch_json(self.url,
                            {'read_position': 41},
                            headers=self.headers)
        record = self.refetch()
        self.assertEqual(record['read_position'], 42)

    def test_read_position_is_saved_if_set_to_higher_value(self):
        self.app.patch_json(self.url,
                            {'read_position': 43},
                            headers=self.headers)
        record = self.refetch()
        self.assertEqual(record['read_position'], 43)

    def test_marked_by_and_on_are_ignored_if_already_unread(self):
        body = {
            'unread': False,
            'marked_read_by': 'Android',
            'marked_read_on': 543210}
        resp = self.app.patch_json(self.url,
                                   body,
                                   headers=self.headers)
        self.assertNotEqual(resp.json['marked_read_by'], 'Android')
        self.assertNotEqual(resp.json['marked_read_on'], 543210)

    def test_timestamp_is_not_updated_if_already_unread(self):
        body = {
            'unread': False,
            'marked_read_by': 'Android',
            'marked_read_on': 543210}
        resp = self.app.patch_json(self.url,
                                   body,
                                   headers=self.headers)
        self.assertEqual(resp.json['last_modified'],
                         self.record['last_modified'])

    def test_body_behavior_is_set_to_full_by_default(self):
        body = {'unread': "True", 'read_position': 10}
        resp = self.app.patch_json(self.url,
                                   body,
                                   headers=self.headers)
        self.assertEqual(set(resp.json.keys()), {
            'added_by', 'added_on', 'archived', 'excerpt', 'favorite', 'id',
            'is_article', 'last_modified', 'marked_read_by', 'marked_read_on',
            'preview', 'read_position', 'resolved_title', 'resolved_url',
            'stored_on', 'title', 'unread', 'url', 'word_count'})

    def test_body_behavior_set_to_diff_return_only_diff(self):
        body = {'unread': "True", 'read_position': 10}
        self.headers.update({
            'Response-Behavior': 'diff'
        })
        resp = self.app.patch_json(self.url,
                                   body,
                                   headers=self.headers)
        self.assertDictEqual(resp.json, {'read_position': 0})

    def test_body_behavior_set_to_light_return_only_changes(self):
        body = {'unread': "True", 'read_position': 10}
        self.headers.update({
            'Response-Behavior': 'light'
        })
        resp = self.app.patch_json(self.url,
                                   body,
                                   headers=self.headers)
        self.assertDictEqual(resp.json, {'unread': True, 'read_position': 0})


class ConflictingArticleTest(BaseWebTest, unittest.TestCase):
    def setUp(self):
        super(ConflictingArticleTest, self).setUp()
        resp = self.app.post_json('/articles',
                                  MINIMALIST_ARTICLE,
                                  headers=self.headers)
        self.before = resp.json
        self.url = '/articles/{id}'.format(id=self.before['id'])

    def test_creating_with_a_conflicting_url_returns_existing(self):
        resp = self.app.post_json('/articles',
                                  MINIMALIST_ARTICLE,
                                  headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertDictEqual(self.before, resp.json)

    def test_creating_with_a_conflicting_resolved_url_returns_existing(self):
        # Just double-check that resolved url was set from url
        self.assertEqual(self.before['resolved_url'], self.before['url'])

        # Try to create another one, with duplicate resolved_url
        record = MINIMALIST_ARTICLE.copy()
        record['resolved_url'] = record['url']
        record['url'] = 'http://bit.ly/abc'

        resp = self.app.post_json('/articles',
                                  record,
                                  headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertDictEqual(self.before, resp.json)

    def test_return_409_on_conflict_with_resolved_url(self):
        record = MINIMALIST_ARTICLE.copy()
        record['url'] = 'https://ssl.mozilla.org'
        resp = self.app.post_json('/articles',
                                  record,
                                  headers=self.headers)
        url = '/articles/{id}'.format(id=resp.json['id'])

        patch = {'resolved_url': MINIMALIST_ARTICLE['url']}
        self.app.patch_json(url,
                            patch,
                            headers=self.headers,
                            status=409)


class DeletedArticleTest(BaseWebTest, unittest.TestCase):
    def setUp(self):
        super(DeletedArticleTest, self).setUp()

        resp = self.app.post_json('/articles',
                                  MINIMALIST_ARTICLE,
                                  headers=self.headers)
        self.before = resp.json
        self.url = '/articles/{id}'.format(id=self.before['id'])
        self.last_modified = self.before['last_modified']
        self.deleted = self.app.delete(self.url, headers=self.headers)

    def test_delete_article_returns_status_deleted(self):
        self.assertEqual(self.deleted.json['deleted'], True)

    def test_deleted_articles_are_marked_with_status_deleted(self):
        resp = self.app.get('/articles?_since=%s' % self.last_modified,
                            headers=self.headers)
        self.assertEqual(resp.json['items'][0]['deleted'], True)

    def test_deleted_articles_are_stripped(self):
        resp = self.app.get('/articles?_since=%s' % self.last_modified,
                            headers=self.headers)
        self.assertEqual(sorted(resp.json['items'][0].keys()),
                         ['deleted', 'id', 'last_modified'])

    def test_url_unicity_does_not_interfere_with_deleted_records(self):
        self.app.post_json('/articles',
                           MINIMALIST_ARTICLE,
                           headers=self.headers)

    def test_deleted_articles_can_be_filtered(self):
        self.app.post_json('/articles',
                           MINIMALIST_ARTICLE,
                           headers=self.headers)
        only_deleted = '/articles?_since=%s&deleted=true' % self.last_modified
        resp = self.app.get(only_deleted,
                            headers=self.headers)
        results = resp.json['items']
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]['deleted'])

    def test_deleted_articles_can_be_sorted_on_deleted_status(self):
        # Create with default status
        self.app.post_json('/articles',
                           MINIMALIST_ARTICLE,
                           headers=self.headers)

        # Create another and archive
        body = MINIMALIST_ARTICLE.copy()
        body['url'] = 'http://host.com'
        resp = self.app.post_json('/articles',
                                  body,
                                  headers=self.headers)
        self.app.patch_json('/articles/%s' % resp.json['id'],
                            {'archived': True},
                            headers=self.headers)

        # Obtain the 3 records
        sort_deleted = '/articles?_since=%s&_sort=deleted' % self.last_modified
        resp = self.app.get(sort_deleted,
                            headers=self.headers)
        records = resp.json['items']
        self.assertEqual(records[0]['deleted'], True)
        self.assertNotIn('deleted', records[1])
