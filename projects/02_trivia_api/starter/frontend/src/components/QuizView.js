import React, { Component } from 'react';
import $ from 'jquery';

import '../stylesheets/QuizView.css';

const questionsPerPlay = 5; 

function PlayerScore(props){
  return(
    <div>
      <h2>{props.player.name}</h2>
      <div className="final-header">Your Final Score is {props.numCorrect}/5</div>
      <div className="final-header">You have played {props.player.games_played} games with a total score of {props.player.total_score}</div>
    </div>
  )
}

function GuesScore(props){
  return(
    <div className="final-header">Your Final Score is {props.numCorrect}/5</div>
  )
}

function ScoreView(props){
  if(props.player_name !== ''){
    return <PlayerScore numCorrect={props.numCorrect} player={props.player}/>;
  }else{
    return <GuesScore numCorrect={props.numCorrect}/>;
  }
}
class QuizView extends Component {
  constructor(props){
    super();
    this.state = {
        quizCategory: null,
        previousQuestions: [], 
        showAnswer: false,
        categories: {},
        numCorrect: 0,
        currentQuestion: {},
        guess: '',
        forceEnd: false,
        player_name:'',
        player: {},
        finalRendered: false
    }
  }

  componentDidMount(){
    $.ajax({
      url: `/categories`, 
      type: "GET",
      success: (result) => {
        this.setState({ categories: result.categories })
        return;
      },
      error: (error) => {
        alert('Unable to load categories. Please try your request again')
        return;
      }
    })
  }

  updatePlayerScore = () => {
    if(this.state.player_name !== ''){
      $.ajax({
        url: `/players`, 
        type: "PATCH",
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify({
          player: this.state.player,
          score_played: this.state.numCorrect
        }),
        xhrFields: {
          withCredentials: true
        },
        crossDomain: true,
        success: (result) => {
          this.setState({ player: result.player })
          return;
        },
        error: (error) => {
          alert('Unable to update player. Please try your request again')
          return;
        }
      })    
    }  
  }

  selectCategory = ({type, id=0}) => {
    if(this.state.player_name !== ''){
      $.ajax({
        url: `/players`, 
        type: "POST",
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify({
          player_name: this.state.player_name
        }),
        xhrFields: {
          withCredentials: true
        },
        crossDomain: true,
        success: (result) => {
          this.setState({ player: result.player })
          return;
        },
        error: (error) => {
          alert('Unable to load player. Please try your request again')
          return;
        }
      })    
    }
    this.setState({quizCategory: {type, id}}, this.getNextQuestion)
  }

  handleChange = (event) => {
    this.setState({[event.target.name]: event.target.value})
  }

  getNextQuestion = () => {
    const previousQuestions = [...this.state.previousQuestions]
    if(this.state.currentQuestion.id) { previousQuestions.push(this.state.currentQuestion.id) }

    $.ajax({
      url: '/quizzes',
      type: "POST",
      dataType: 'json',
      contentType: 'application/json',
      data: JSON.stringify({
        previous_questions: previousQuestions,
        quiz_category: this.state.quizCategory
      }),
      xhrFields: {
        withCredentials: true
      },
      crossDomain: true,
      success: (result) => {
        this.setState({
          showAnswer: false,
          previousQuestions: previousQuestions,
          currentQuestion: result.question,
          guess: '',
          forceEnd: result.question ? false : true
        })
        return;
      },
      error: (error) => {
        alert('Unable to load question. Please try your request again')
        return;
      }
    })
  }

  submitGuess = (event) => {
    event.preventDefault();
    const formatGuess = this.state.guess.replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g,"").toLowerCase()
    let evaluate =  this.evaluateAnswer()
    this.setState({
      numCorrect: !evaluate ? this.state.numCorrect : this.state.numCorrect + 1,
      showAnswer: true,
    })
  }

  restartGame = () => {
    this.setState({
      quizCategory: null,
      previousQuestions: [], 
      showAnswer: false,
      numCorrect: 0,
      currentQuestion: {},
      guess: '',
      forceEnd: false
    })
  }

  handleChange = (event) => {
    this.setState({[event.target.name]: event.target.value})
  }

  renderPrePlay(){
      return (
          <div className="quiz-play-holder">
              <div className="choose-header">Enter Player name</div>
              <label>
                Player name
                <input type="text" name="player_name" onChange={this.handleChange}/>
              </label>
              <div className="choose-header">Choose Category</div>
              <div className="category-holder">
                  <div className="play-category" onClick={this.selectCategory}>ALL</div>
                  {Object.keys(this.state.categories).map(id => {
                  return (
                    <div
                      key={id}
                      value={id}
                      className="play-category"
                      onClick={() => this.selectCategory({type:this.state.categories[id], id})}>
                      {this.state.categories[id]}
                    </div>
                  )
                })}
              </div>
          </div>
      )
  }

  renderFinalScore(){

    if(!this.state.finalRendered){
      this.updatePlayerScore();
      this.setState({ finalRendered: true });
    }

    return(
      <div className="quiz-play-holder">
        <ScoreView player_name={this.state.player_name} player={this.state.player} numCorrect={this.state.numCorrect}/>
        <div className="play-again button" onClick={this.restartGame}> Play Again? </div>
      </div>
    )
  }

  evaluateAnswer = () => {
    const formatGuess = this.state.guess.replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g,"").toLowerCase()
    const answerArray = this.state.currentQuestion.answer.toLowerCase().split(' ');
    return answerArray.includes(formatGuess)
  }

  renderCorrectAnswer(){
    const formatGuess = this.state.guess.replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g,"").toLowerCase()
    let evaluate =  this.evaluateAnswer()
    return(
      <div className="quiz-play-holder">
        <div className="quiz-question">{this.state.currentQuestion.question}</div>
        <div className={`${evaluate ? 'correct' : 'wrong'}`}>{evaluate ? "You were correct!" : "You were incorrect"}</div>
        <div className="quiz-answer">{this.state.currentQuestion.answer}</div>
        <div className="next-question button" onClick={this.getNextQuestion}> Next Question </div>
      </div>
    )
  }

  renderPlay(){
    return this.state.previousQuestions.length === questionsPerPlay || this.state.forceEnd
      ? this.renderFinalScore()
      : this.state.showAnswer 
        ? this.renderCorrectAnswer()
        : (
          <div className="quiz-play-holder">
            <div className="quiz-question">{this.state.currentQuestion.question}</div>
            <form onSubmit={this.submitGuess}>
              <input type="text" name="guess" onChange={this.handleChange}/>
              <input className="submit-guess button" type="submit" value="Submit Answer" />
            </form>
          </div>
        )
  }


  render() {
    return this.state.quizCategory
        ? this.renderPlay()
        : this.renderPrePlay()
  }
}

export default QuizView;
