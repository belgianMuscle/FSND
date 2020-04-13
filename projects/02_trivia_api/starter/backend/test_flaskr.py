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
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'udacity','localhost:5432', self.database_name)
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

    """
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['categories'])

    def test_get_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['current_category']=='')

    def test_delete_question(self):
        res = self.client().delete('/questions/2')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
    
    def test_create_question(self):
        res = self.client().post('/questions',data=json.dumps({
            'question':'Unit test',
            'answer':'test',
            'difficulty':3,
            'category':'4'
        }),content_type='application/json')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['question'])

    def test_get_question_for_category(self):
        res = self.client().get('/categories/4/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])
        self.assertTrue(len(data['questions'])==data['total_questions'])

    def test_search_questions(self):
        res = self.client().post('/questions/search',data=json.dumps({
            'searchTerm':'test'
        }), content_type="application/json")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['search_term'])
        self.assertTrue(data['current_category']=='')
        self.assertTrue(len(data['questions'])==data['total_questions'])
    
    def test_quizzes(self):
        res = self.client().post('/quizzes',data=json.dumps({
            'previous_questions':[1,2,3],
            'quiz_category':{'id':'4'}
        }), content_type="application/json")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['question'])

    def test_create_category(self):
        res = self.client().post('/categories',data=json.dumps({
            'type':'Unit test'
        }),content_type='application/json')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['category'])

    def test_rate_question(self):
        res = self.client().patch('/questions/5',data=json.dumps({
            'new_rating':4
        }),content_type='application/json')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['question'])


    def test_create_player(self):
        res = self.client().post('/players',data=json.dumps({
            'player_name':'Unittest'
        }),content_type='application/json')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['player'])

    
    def test_get_player(self):
        res = self.client().post('/players',data=json.dumps({
            'player_name':'Unittest'
        }),content_type='application/json')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['player'])

    
    def test_update_player_score(self):
        res = self.client().patch('/players',data=json.dumps({
            'player':{'id':1,'name':'Unittest'},
            'score_played':3
        }),content_type='application/json')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['player'])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()