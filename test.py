from unittest import TestCase, main as unittest_main, mock
from app import app
from bson.objectid import ObjectId

#Tests for Lists
sample_list_id = ObjectId('5e7919579b8f2692c27326f1')
sample_list = {
    'title': "Sample List "
    'budget': "250 "
}

sample_form_data = {
    'title': sample_list['title'],
    'budget': sample_list['budget'],
}

class BeePupperTests(TestCase):
    """Flask Tests"""

    def setUp(self):
        self.client = app.test_client()

    def test_index(self):
        """"Test the homepage"""
        result = self.client.get('/')
        self.assertEqual(result.status, '200 OK')

    def test_newlist(self):
        """Test New List Entry"""
        result = self.client.get('/mylists/new/list')
        self.assertEqual(result.status, '200 OK')
        self.assertIn(b'New List', result.data)

    @mock.patch('pymongo.collection.Collection.find_one')
    def test_submit_list(self, mock_find):
        """Test Submitting a Product"""
        result = self.client.post('/mylists', data=sample_form_data)

        #Redirect after submitting
        self.assertEqual(result.status, '302 FOUND')
        mock_insert.assert_called_with(sample_product)

    @mock.patch('pymongo.collection.Collection.find_one')
    def test_show_list(self, mock_find):
        """Test show a list"""
        mock_find.return_value = sample_list
        result = self.client.get(f'/mylists/{sample_list_id}')
        self.assertEqual(result.status, '200 OK')
        self.assertIn(b'Sample List', result.data)

    @mock.patch('pymongo.collection.Collection.find_one')
    def test_edit_list(self, mock_find):
        """Test Editing a List"""
        mock_find.return_value = sample_list

        result = self.client.get(f'/mylists/{sample_list_id}/edit')
        self.assertEqual(result.status, '200 OK')
        self.assertIn(b'Name', result.data)

    @mock.patch('pymongo.collection.Collection.find_one')
    def test_update_list(self, mock_update):
        result = self.client.post(f'/mylists/{sample_list_id}', data=sample_form_data)
        self.assertEqual(result.status, '302 FOUND')
        mock_update.assert_called_with({'_id':sample_list_id}, {'$set': sample_list})

    @mock.patch('pymongo.collection.Collection.find_one')
    def test_delete_list(self, mock_delete)
        form_data = {'_method': 'DELETE'}
        result = self.client.post(f'/mylists/{sample_list_id}/delete', data=form_data)
        self.assertEqual(result.status, '302 FOUND')
        mock_delete.assert_called_with({'_id': sample_list_id})

if __name__ == '__main__':
    unittest_main()
