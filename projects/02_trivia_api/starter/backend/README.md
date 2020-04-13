# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### React

This project uses the React to function. To install, run the following command

```bash
npm install --save react
```

#### React-Rating

This project uses the React-Rating module for rating questions. All that is necessary is to ensure React-rating is installed.

```bash
npm install --save react-rating
```

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 
3. Create an endpoint to handle GET requests for all available categories. 
4. Create an endpoint to DELETE question using a question ID. 
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 
6. Create a POST endpoint to get questions based on category. 
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 
9. Create error handlers for all expected errors including 400, 404, 422 and 500. 



## API Documentation

### Categories
#### GET '/categories'
```
GET '/categories'
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains a object of id: category_string key:value pairs. 
{
    'categories':{'1' : "Science",
                '2' : "Art",
                '3' : "Geography",
                '4' : "History",
                '5' : "Entertainment",
                '6' : "Sports"}
}
```
#### POST '/categories'
```
POST '/categories'
- Creates a new category in the database
- Request Data: dictionary with key 'type' containing the category type text
- Returns: An object containing a single key, category, that contains a category object containing id: category_string key:value pairs. 
{
    'category':{'1' : "Science"}
}
```
#### GET '/categories/<category_id>/questions'
```
GET '/categories/<category_id>/questions'
- Returns all questions for a given category 
- Route Argument: category_id
- Returns: An object containing a keys: questions, total_questions, current_category  
{
    'questions':[{'id' : "1",
            'question': "Question?",
            'answer':'Answer',
            'difficulty':1,
            'category':1,
            'no_of_ratings':0,
            'total_ratings':0,
            'rating':0}],
    'total_questions':1,
    'current_category':1
 }
```

### Questions
#### GET '/questions'
```
GET '/questions'
- Fetches a list of questions for a single page of 10 records
- Request Arguments: page (optional)
- Returns: An object with a with keys: questions (list of question objects), total_questions (amount of total questions), categories (category object containing key-value pair list of all categories) and current_category as blank 
{
    'questions':[],
    'total_questions':20,
    'categories':{'1' : "Science",
                '2' : "Art",
                '3' : "Geography",
                '4' : "History",
                '5' : "Entertainment",
                '6' : "Sports"},
    'current_category':''
}
```
#### DELETE '/questions/<question_id>'
```
DELETE '/questions/<question_id>'
- Deletes a question record for the given question_id
- Route argument: question_id
- Returns: an object with success value set to True
```
#### POST '/questions'
```
POST '/questions'
- Creates a new question
- Request Data: dictionary with keys: question, answer, difficulty and category
- Returns: An object containing a single key, question, that contains a Question object  
{
    'question':{'id' : "1",
            'question': "Question?",
            'answer':'Answer',
            'difficulty':1,
            'category':1,
            'no_of_ratings':0,
            'total_ratings':0,
            'rating':0}
 }
```
#### PATCH '/questions/<question_id'>
```
PATCH '/questions/<question_id>'
- Updates rating of the given question_id
- Request Data: dictionary with single key: new_rating
- Route argument: question_id
- Returns: An object containing a single key, question, that contains a Question object  
{
    'question':{'id' : "1",
            'question': "Question?",
            'answer':'Answer',
            'difficulty':1,
            'category':1,
            'no_of_ratings':0,
            'total_ratings':0,
            'rating':0}
 }
```
#### POST '/questions/search'
```
PATCH '/questions/search'
- Search for questions with text containing given search term
- Request Data: dictionary with single key: searchTerm
- Returns: An object containing a keys: questions, total_questions, search_term, current_category  
{
    'questions':[{'id' : "1",
            'question': "Question?",
            'answer':'Answer',
            'difficulty':1,
            'category':1,
            'no_of_ratings':0,
            'total_ratings':0,
            'rating':0}],
    'total_questions':1,
    'search_term':'question',
    'current_category':''
 }
```

### Quizzes
#### POST '/quizzes'
```
POST '/quizzes'
- Returns a new question to play the quizz, this endpoint ensures you are given a question that has not yet been played
  and is part of the category if provided.
- Request data: dictionary with keys: quiz_category (id of the category), pervious_questions (list of ids of questions already played)
- Returns: An object containing a single key: question if a new question was found
{
    'question':{'id' : "1",
            'question': "Question?",
            'answer':'Answer',
            'difficulty':1,
            'category':1,
            'no_of_ratings':0,
            'total_ratings':0,
            'rating':0}
 }
```

### Players
#### POST '/players'
```
POST '/players'
- Creates a new player or returns an existing player if the name already exists
- Request Data: dictionary with key 'name' containing the name of the player
- Returns: An object containing a single key, player, that contains a Player object  
{
    'player':{'id' : "1",
            'name': "player",
            'games_played':2,
            'total_score':6}
 }
```
#### PATCH '/players'
```
PATCH '/players'
- Adds a new game with score obtained to the player's total scores
- Request Data: A player object, containing dictionary fields and a 'score_played' value
- Returns: A player object containing id:player_id, name:player_name, games_played:number of games played and total_score:total score from all games. 
{'id' : "1",
 'name': "player",
 'games_played':2,
 'total_score':6}
```

### Error Codes

- 404: Resource not found
- 405: Method not allowed
- 422: Resrouce cannot be processed
- 400: Bad request
- 500: Request not allowed


## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```