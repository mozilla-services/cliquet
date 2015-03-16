import colander

from readinglist.views.article import ArticleSchema

from .support import unittest


class ArticleSchemaTest(unittest.TestCase):
    def setUp(self):
        self.schema = ArticleSchema()
        self.schema = self.schema.bind()
        self.record = dict(title="We are Charlie",
                           url="http://charliehebdo.fr",
                           added_by="FxOS")
        self.deserialized = self.schema.deserialize(self.record)

    def test_record_validation(self):
        self.assertEqual(self.deserialized['title'], self.record['title'])

    def test_record_validation_default_values(self):
        self.assertEqual(self.deserialized['excerpt'], '')
        self.assertEqual(self.deserialized['archived'], False)
        self.assertEqual(self.deserialized['favorite'], False)
        self.assertEqual(self.deserialized['unread'], True)
        self.assertEqual(self.deserialized['is_article'], True)
        self.assertEqual(self.deserialized['read_position'], 0)
        self.assertIsNone(self.deserialized.get('preview'))
        self.assertIsNone(self.deserialized.get('marked_read_by'))
        self.assertIsNone(self.deserialized.get('marked_read_on'))
        self.assertIsNone(self.deserialized.get('word_count'))
        self.assertIsNone(self.deserialized.get('resolved_url'))
        self.assertIsNone(self.deserialized.get('resolved_title'))

    def test_record_validation_computed_values(self):
        self.assertIsNotNone(self.deserialized.get('stored_on'))
        self.assertIsNotNone(self.deserialized.get('added_on'))
        self.assertIsNotNone(self.deserialized.get('last_modified'))

    def test_url_is_required(self):
        self.record.pop('url')
        self.assertRaises(colander.Invalid,
                          self.schema.deserialize,
                          self.record)

    def test_url_is_stripped(self):
        self.record['url'] = '  http://charliehebdo.fr'
        deserialized = self.schema.deserialize(self.record)
        self.assertEqual(deserialized['url'], 'http://charliehebdo.fr')

    def test_resolved_url_is_stripped(self):
        self.record['resolved_url'] = '  http://charliehebdo.fr'
        deserialized = self.schema.deserialize(self.record)
        self.assertEqual(deserialized['resolved_url'],
                         'http://charliehebdo.fr')

    def test_url_has_max_length(self):
        self.record['url'] = 'http://charliehebdo.fr/#' + ('a' * 2048)
        self.assertRaises(colander.Invalid,
                          self.schema.deserialize,
                          self.record)

    def test_resolved_url_has_max_length(self):
        self.record['resolved_url'] = 'http://charliehebdo.fr/#' + ('a' * 2048)
        self.assertRaises(colander.Invalid,
                          self.schema.deserialize,
                          self.record)

    def test_title_is_required(self):
        self.record.pop('title')
        self.assertRaises(colander.Invalid,
                          self.schema.deserialize,
                          self.record)

    def test_title_is_stripped(self):
        self.record['title'] = '  Nous Sommes Charlie  '
        deserialized = self.schema.deserialize(self.record)
        self.assertEqual(deserialized['title'], 'Nous Sommes Charlie')

    def test_title_max_length_represents_characters_not_bytes(self):
        self.record['title'] = u'\u76d8' * 1024
        self.schema.deserialize(self.record)  # not raising

    def test_title_has_max_length(self):
        self.record['title'] = u'\u76d8' * 1025
        deserialized = self.schema.deserialize(self.record)
        self.assertEqual(len(deserialized['title']), 1024)

    def test_resolved_title_has_max_length(self):
        self.record['resolved_title'] = u'\u76d8' * 1025
        deserialized = self.schema.deserialize(self.record)
        self.assertEqual(len(deserialized['resolved_title']), 1024)

    def test_resolved_title_is_stripped(self):
        self.record['resolved_title'] = '  Nous Sommes Charlie  '
        deserialized = self.schema.deserialize(self.record)
        self.assertEqual(deserialized['resolved_title'], 'Nous Sommes Charlie')

    def test_title_must_be_at_least_one_character(self):
        self.record['title'] = ''
        self.assertRaises(colander.Invalid,
                          self.schema.deserialize,
                          self.record)

    def test_resolved_title_must_be_at_least_one_character(self):
        self.record['resolved_title'] = ' '
        self.assertRaises(colander.Invalid,
                          self.schema.deserialize,
                          self.record)

    def test_added_by_is_required(self):
        self.record.pop('added_by')
        self.assertRaises(colander.Invalid,
                          self.schema.deserialize,
                          self.record)

    def test_added_by_must_be_at_least_one_character(self):
        self.record['added_by'] = ''
        self.assertRaises(colander.Invalid,
                          self.schema.deserialize,
                          self.record)

    def test_marked_read_by_must_be_at_least_one_character(self):
        self.record['marked_read_by'] = ' '
        self.assertRaises(colander.Invalid,
                          self.schema.deserialize,
                          self.record)

    def test_read_position_must_be_positive(self):
        self.record['read_position'] = -1
        self.assertRaises(colander.Invalid,
                          self.schema.deserialize,
                          self.record)

    def test_archived_is_coerced_into_boolean(self):
        self.record['archived'] = 'false'
        deserialized = self.schema.deserialize(self.record)
        self.assertFalse(deserialized['archived'])

    def test_status_is_ignored(self):
        self.record['status'] = 2
        deserialized = self.schema.deserialize(self.record)
        self.assertNotIn('status', deserialized)

    def test_deleted_is_ignored(self):
        self.record['deleted'] = 'true'
        deserialized = self.schema.deserialize(self.record)
        self.assertNotIn('deleted', deserialized)

    def test_preview_can_be_specified(self):
        self.record['preview'] = 'http://server/image.jpg'
        deserialized = self.schema.deserialize(self.record)
        self.assertEqual(deserialized['preview'], 'http://server/image.jpg')

    def test_preview_should_be_a_valid_url(self):
        self.record['preview'] = '4AAQSkZJRgABAQAQ'
        self.assertRaises(colander.Invalid,
                          self.schema.deserialize,
                          self.record)

    def test_preview_has_max_length(self):
        self.record['preview'] = 'http://server/image' + ('a' * 2048)
        self.assertRaises(colander.Invalid,
                          self.schema.deserialize,
                          self.record)

    def test_preview_can_be_under_any_protocol(self):
        self.record['preview'] = 'http2://server/image.jpg'
        deserialized = self.schema.deserialize(self.record)
        self.assertEqual(deserialized['preview'], 'http2://server/image.jpg')

    def test_preview_can_be_an_empty_string(self):
        self.record['preview'] = ''
        deserialized = self.schema.deserialize(self.record)
        self.assertIsNone(deserialized['preview'])
