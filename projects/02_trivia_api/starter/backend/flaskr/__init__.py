import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, Player

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  app.config['DEBUG'] = True 
  app.config['TESTING'] = True

  '''
  Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  Use the after_request decorator to set Access-Control-Allow
  '''
  CORS(app,resources={r"*": {"origins": "*"}})

  # CORS Headers 
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,PATCH')
      return response

  '''
  Endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories',methods=['GET'])
  def get_categories():
    
    categories_result = Category.query.all()

    if len(categories_result) == 0:
          abort(404)

    categories = {}
    for category in categories_result:
        categories[category.id]=category.type

    return jsonify({
      'success':True,
      'categories':categories
    })

  '''
  Endpoint to handle POST requests to create new category
  '''
  @app.route('/categories',methods=['POST'])
  def create_category():
    data = request.get_json()

    category = Category(data['type'])

    category.insert()

    return jsonify({
      'success':True,
      'category':category.format()
    })
  
  '''
  Endpoint to handle POST requests to create new player or return existing one
  '''
  @app.route('/players',methods=['POST'])
  def get_or_create_player():
    data = request.get_json()

    player = Player.query.filter(Player.name == data['player_name']).one_or_none()

    if not player:
      player = Player(data['player_name'])
      player.insert()

    return jsonify({
      'success':True,
      'player':player.format()
    })

  @app.route('/players',methods=['PATCH'])
  def update_player():
    data = request.get_json()

    player = Player.query.get(data['player']['id'])

    if player:
      player.addGame(data['score_played'])
    else:
      abort(404)

    return jsonify({
      'success':True,
      'player':player.format()
    })

  '''
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions',methods=['GET'])
  def get_questions():
    page = request.args.get('page', 1, type=int)

    questions_page = Question.query.paginate(page,QUESTIONS_PER_PAGE,False)
    categories_result = Category.query.all()

    if len(questions_page.items) == 0:
          abort(404)

    questions = [question.format() for question in questions_page.items]

    categories = {}
    for category in categories_result:
        categories[category.id]=category.type

    return jsonify({
      'success':True,
      'questions':questions,
      'total_questions':questions_page.total,
      'categories':categories,
      'current_category':''
    })

  '''
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<question_id>',methods=['DELETE'])
  def delete_question(question_id):

    question = Question.query.get(question_id)

    if not question:
          abort(404)

    question.delete()

    return jsonify({
      'success':True
    })

  '''
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions',methods=['POST'])
  def create_question():
    data = request.get_json()

    question = Question(data['question'],data['answer'],data['difficulty'],data['category'])

    question.insert()

    return jsonify({
      'success':True,
      'question':question.format()
    })

  '''
  Create an endpoint to PATCH an existing question to update the rating
  '''
  @app.route('/questions/<question_id>',methods=['PATCH'])
  def update_question(question_id):
    data = request.get_json()

    question = Question.query.get(question_id)

    if not question:
      abort(404)

    question.addRating(data['new_rating'])

    return jsonify({
      'success':True,
      'question':question.format()
    })

  '''
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search',methods=['POST'])
  def search_question():
    data = request.get_json()

    question_results = Question.query.filter(Question.question.ilike(f'%{data["searchTerm"]}%')).all()

    if len(question_results)==0:
      abort(404)

    questions = [question.format() for question in question_results]

    return jsonify({
      'success':True,
      'questions':questions,
      'total_questions':len(questions),
      'search_term':data['searchTerm'],
      'current_category':''
    }) 

  '''
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<category_id>/questions',methods=['GET'])
  def get_questions_by_category_id(category_id):
    category = Category.query.get(category_id)
    if not category:
      abort(404)

    questions = Question.query.filter(Question.category == category.id).all()

    question_list = [question.format() for question in questions]

    return jsonify({
      'success':True,
      'questions':question_list,
      'total_questions':len(questions),
      'current_category':category.id
    })   

  '''
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes',methods=['POST'])
  def get_quizz():
    data = request.get_json()

    category = data['quiz_category']
    previousQuestionsList = data['previous_questions']

    if category:
      question = Question.query.filter(Question.category == category['id']).filter(Question.id.notin_(previousQuestionsList)).limit(1).one_or_none()
    else:
      question = Question.query.filter(Question.id.notin_(previousQuestionsList)).limit(1).one_or_none()
    

    if question:
      return jsonify({
        'success':True,
        'question':question.format(),
      })
    else:
      return jsonify({
        'success':False
      })    


  '''
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          'success': False,
          'message': 'Resource not found',
          'error':404
      }),404

  @app.errorhandler(405)
  def not_found(error):
      return jsonify({
          'success':False,
          'message':'Method not allowed',
          'error':405
      }),405

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          'success':False,
          'message':'Resource cannot be processed',
          'error':422
      }),422


  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          'success':False,
          'message':'Bad reqeust',
          'error':400
      }),400

  @app.errorhandler(500)
  def bad_request(error):
      return jsonify({
          'success':False,
          'message':'Request not allowed',
          'error':500
      }),500
  
  return app

    