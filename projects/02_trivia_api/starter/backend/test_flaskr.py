import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path='postgresql://postgres:sadsel2525@localhost:5432/{}'.format(self.database_name)
        # self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_delete_question(self):
        res=self.client().delete('/question/api/22')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)


    def test_of_fail_delete_question(self):
        res = self.client().delete('/question/api/3')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)

    def test_get_categories(self):
        res=self.client().get('/data/api/categories')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertTrue(len(data['categories']))
    def test_fail_get_categories(self):
        res=self.client().get('/data/api/categories')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertTrue(len(data['categories']))
    def test_get_questions_of_specific_category(self):
        res=self.client().get('/categories/1/questions')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertTrue(len(data['questions']))
    def test_404_sent_requesting_beyond_valid_page(self):
        res=self.client().get('/data/api/questions/?page=1000')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'Not Found')
    def test_get_questions(self):
        res=self.client().get('/data/api/questions/?page=1')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
    def test_submit_question(self):
        res=self.client().post('data/api/question',json={ 'question': 'how?',
        'answer': 'no',
        'difficulty': 1,
        'category': '1'})
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
    def test_fail_submit_question(self):
        res=self.client().post('data/api/question',json={'question': '',
        'answer': 'no',
        'difficulty': 1,
        'category': '1'})
        data=json.loads(res.data)
        self.assertEqual(data['success'],False)


    def test_play_request(self):
        res=self.client().post('/play/api/questions',json={
        "previous_questions": [],
        "quiz_category": {"type": "click", "id": 0}})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    def test_fail_play_request(self):
        res=self.client().post('/play/api/questions',json={
        "previous_questions": [],
        "quiz_category": {"type": "thriller", "id": 10}})

        data = json.loads(res.data)
        self.assertEqual(data["error"],500)

    def test_search_for_question(self):
        res=self.client().post('/question/api/find/?term=i')
        data = json.loads(res.data)
        self.assertTrue(len(data['questions']))

    def test_search_for_question(self):
        res=self.client().post('/question/api/find/?term=.')
        data = json.loads(res.data)
        self.assertFalse(len(data['questions']))


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()