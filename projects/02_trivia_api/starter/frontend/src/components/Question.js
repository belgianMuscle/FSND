import React, { Component } from 'react';
import '../stylesheets/Question.css';
import Rating from 'react-rating';
import $ from 'jquery';

class Question extends Component {
  constructor(){
    super();
    this.state = {
      visibleAnswer: false
    }
  }

  flipVisibility() {
    this.setState({visibleAnswer: !this.state.visibleAnswer});
  }

  render() {
    const { key, question, answer, category, difficulty, question_rating } = this.props;
    return (
      <div className="Question-holder">
        <div className="Question">{question}</div>
        <div className="Question-status">
          <img className="category" src={`${category}.svg`}/>
          <div className="difficulty">Difficulty: {difficulty}</div>

          <Rating 
            emptySymbol="fa fa-star"
            fullSymbol="fa fa-star checked"
            initialRating={question_rating}
            onChange={(value) => this.props.questionRating(value)}
          />

          <img src="delete.png" className="delete" onClick={() => this.props.questionAction('DELETE')}/>
        </div>
        <div className="show-answer button"
            onClick={() => this.flipVisibility()}>
            {this.state.visibleAnswer ? 'Hide' : 'Show'} Answer
        </div>
        <div className="answer-holder">
          <span style={{"visibility": this.state.visibleAnswer ? 'visible' : 'hidden'}}>Answer: {answer}</span>
        </div>
      </div>
    );
  }
}

export default Question;
