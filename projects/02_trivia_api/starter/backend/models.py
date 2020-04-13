import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
import json

database_name = "trivia"
database_path = "postgres://{}:{}@{}/{}".format('postgres', 'udacity','localhost:5432', database_name)
        

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

'''
Question

'''
class Question(db.Model):  
  __tablename__ = 'questions'

  id = Column(Integer, primary_key=True)
  question = Column(String)
  answer = Column(String)
  category = Column(String)
  difficulty = Column(Integer)
  no_of_ratings = Column(Integer)
  total_ratings = Column(Integer)
  rating = Column(Integer)

  def __init__(self, question, answer, category, difficulty,no_of_ratings=0,total_ratings=0,rating=0):
    self.question = question
    self.answer = answer
    self.category = category
    self.difficulty = difficulty
    self.no_of_ratings = no_of_ratings
    self.total_ratings = total_ratings
    self.rating = rating

  def insert(self):
    db.session.add(self)
    db.session.commit()
  
  def update(self):
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  def addRating(self,newRating):
    print(self.format())
    self.total_ratings = self.total_ratings + newRating
    self.no_of_ratings = self.no_of_ratings + 1
    self.rating = self.total_ratings / self.no_of_ratings
    db.session.commit()

  def format(self):
    return {
      'id': self.id,
      'question': self.question,
      'answer': self.answer,
      'category': self.category,
      'difficulty': self.difficulty,
      'no_of_ratings':self.no_of_ratings,
      'total_ratings':self.total_ratings,
      'rating':self.rating
    }

'''
Category

'''
class Category(db.Model):  
  __tablename__ = 'categories'

  id = Column(Integer, primary_key=True)
  type = Column(String)

  def __init__(self, type):
    self.type = type

  def insert(self):
    db.session.add(self)
    db.session.commit()

  def format(self):
    return {
      'id': self.id,
      'type': self.type
    }

class Player(db.Model):
  __tablename__ = 'players'

  id = Column(Integer, primary_key=True)
  name = Column(String(25))
  games_played = Column(Integer)
  total_score = Column(Integer)

  def __init__(self, name, games_played=0, total_score=0):
    self.name = name
    self.games_played = games_played
    self.total_score = total_score

  def insert(self):
    db.session.add(self)
    db.session.commit()
  
  def addGame(self,score):
    self.games_played = self.games_played + 1
    self.total_score = self.total_score + score
    db.session.commit()

  def update(self):
    db.session.commit()

  def format(self):
        return {
      'id': self.id,
      'name': self.name,
      'games_played':self.games_played,
      'total_score':self.total_score
    }