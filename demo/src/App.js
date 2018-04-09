import React, { Component } from 'react';
import './App.css';
import TextUnits from './TextUnit.js'
import Summary from './Summary.js'
import Paragraphs from './Paragraph.js'
import axios from 'axios';
import {Col, Row, Grid} from 'react-bootstrap'

var headers = {
         'Content-Type': 'application/json',
}      

class Form extends Component{
  constructor(props){
    super(props);
    this.props = props;
    this.state = {'url':"", 'show':true,
              judged_num:null,
              total_num:null,
    };
    this.randomUrl = this.randomUrl.bind(this);
    this.onhideBoilerPlate = this.onhideBoilerPlate.bind(this);
    this.handleFormChange = this.handleFormChange.bind(this);
    this.updateStatistic = this.updateStatistic.bind(this);
  }

  randomUrl(type){
    axios.get("http://stcvm-linux22:5903/random_one?type=" + type).then((res) => 
        {
          this.setState({"url":res.data.url});
          this.input.value = res.data.url;
        }
    )
  }

  updateStatistic(){
    axios.get("http://stcvm-linux22:5903/statistic").then((res) => 
        {
          this.setState({"total_num":res.data.total_num,
                        "judged_num":res.data.judged_num
          });
        }
    )
  }
  componentDidMount(){
      this.updateStatistic()
  }

  handleFormChange(event){
    event.preventDefault();
    this.props.handleFormChange(this.input.value);
  }

  onhideBoilerPlate(event){
    this.setState({'show':!this.state.show})
    this.props.handleShowHide();
  }


  render(){
    return (
      <div>
        <form onSubmit={this.handleFormChange}>
            <input
              type="text"
              ref={(input) => this.input = input}
              onChange={(event) => {this.props.handleUrlChange(event.target.value)}}
              style={{"width":"400px"}}
              />
          <input type="submit" value="Submit" />
        </form>
        <div class="buttons">
          <input type="label" class="stats" value={"Total_#:" + this.state.total_num}/>
          <input type="label" class="stats" value={"Judged#:" + this.state.judged_num}/>
        </div>
        <div class="buttons">
              <input type="button" value="GotoUrl" onClick={(event) => {window.open(this.input.value)}}/>
              <input type="button" value={this.state.show? "HideBoilerPlate" : "ShowBoilerPlate"} onClick={this.onhideBoilerPlate} ref={(input) => {this.hideInput = input}}/>
        </div>
        <div class="buttons">
          <input type="button" value="RandomUrl(UnJudged)" onClick={()=>this.randomUrl(0)}/>
          <input type="button" value="RandomUrl(Judged)" onClick={()=>this.randomUrl(1)}/>
        </div>
        <div class="buttons">
          <input type="button" value="SaveJudge" onClick={this.props.handleSaveJudge}/>
          <input type="button" value="LoadJudge" onClick={this.props.handleLoadJudge}/>
        </div>
      </div>
    )
  }
}


class App extends Component {
  constructor(props){
    super(props);
    this.state = {
      url:"",
      paragraphs:null,
      textunits:null,
      summary:null,
      labels:null,
      show_boilerplate:true
    }
    this.handleFormChange = this.handleFormChange.bind(this);
    this.handleUrlChange = this.handleUrlChange.bind(this);
    this.handleShowHide = this.handleShowHide.bind(this);
    this.handleSaveJudge = this.handleSaveJudge.bind(this);
    this.handleLoadJudge = this.handleLoadJudge.bind(this);
  }

  handleLoadJudge(event){
    if (this.state.url === ""){
        alert("Please: \n 1. Randome one judged url \n 2. Then submit this url") 
        return 
    }
    var json_d = {"url":this.state.url}
    axios.post("http://stcvm-linux22:5903/load_judge", json_d, headers).then(
      (res) =>{
          if (res.data.textunits !== null){
              this.setState({"textunits":res.data.textunits, 
                            "labels": res.data.labels             
            })
          }
      })
  }

  handleSaveJudge(event){
    if (this.state.url === ""){
        alert("Null Url") 
        return 
    }
    //var data = JSON.stringify(this.refs.textunits.textunits_labels);
    var json_d = {"url":this.state.url, "textunits":this.state.textunits, "labels":this.refs.textunits.labels}
    axios.post("http://stcvm-linux22:5903/save_judge", json_d, headers).then(
      (res) =>{
          res.data.success?
          alert("Succeed!"):
          alert("Failed")
          this.refs.form.updateStatistic()
      }

      )
  }

  handleUrlChange = (url) => {
    this.setState({url:url})
  }

  handleFormChange = (url) => {
    var headers = {
             'Content-Type': 'application/json',
    }      
    var data = {url:url}
    axios.post("http://stcvm-linux22:5903/summary", data, headers)
     .then(
         res => {

                  this.setState({paragraphs: res.data.paragraphs,
                  textunits:res.data.textunits,
                  summary:res.data.summary,
                  url:url,
                  labels:null,
                  judged_num:res.data.judged_num,
                  total_num:res.data.total_num
              });
         }
     ).catch(err => {
         console.log(err);
     });
  }

  handleShowHide = (event) => {
    this.setState({show_boilerplate: !this.state.show_boilerplate})
  }

  render() {
    return (
      <Grid>
        <Row>
            <h2 class='headline'> Deep Comparison</h2>
            <Form handleFormChange={this.handleFormChange} 
                  handleUrlChange={this.handleUrlChange} 
                  handleShowHide={this.handleShowHide}
                  handleSaveJudge={this.handleSaveJudge}
                  handleLoadJudge={this.handleLoadJudge}
                  ref="form"
            />
        </Row>
        <Row>
          <Col md={4} lg={4}>
            <Paragraphs paragraphs={this.state.paragraphs} show_boilerplate={this.state.show_boilerplate}/>
          </Col>
          <Col md={4} lg={4}>
            <TextUnits textunits={this.state.textunits} url={this.state.url} labels={this.state.labels} ref="textunits"/>
          </Col>
          <Col md={4} lg={4}>
            <Summary summary={this.state.summary}/>
          </Col>
        </Row>
      </Grid>
    );
  }
}

export default App;
