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

//var urlPrefix = "http://stcvm-linux22:5904"
var urlPrefix = ""

class Form extends Component{
  constructor(props){
    super(props);
    this.props = props;
    this.state = {'url':"", 'show':true,
              judged_num:null,
              total_num:null,
              stats:null,
              querysetIdx:0,
    };
    this.randomUrl = this.randomUrl.bind(this);
    this.handleFormChange = this.handleFormChange.bind(this);
    this.updateStatistic = this.updateStatistic.bind(this);
  }

  randomUrl(type){
    var json_d = {"type":type,"tagidx":this.state.querysetIdx, "signature":this.refs.signature?this.refs.signature.value:""}
    var that = this
    axios.post(urlPrefix + "/random_one", json_d, headers).then((res) =>
        {
          that.setState({"url":res.data.url});
          that.input.value = res.data.url;
        }
    )
  }

  updateStatistic(){
    var json_d = {"signature":this.refs.signature?this.refs.signature.value:""}
    axios.post(urlPrefix + "/statistic", json_d, headers).then((res) =>
        {
          this.setState(
            {"stats":res.data}
          );
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

  render(){
    return (
      <div class='searchbar'>
            <input
              ref={(input) => this.input = input}
              style={{"width":"500px"}}
              />
          <input type="submit" value="Submit" class='button' onClick={this.handleFormChange}/>
          <input type="button" value="GotoUrl" class='button' onClick={(event) => {window.open(this.input.value)}}/>
            {
                this.state.stats === null?
                null:
                <div style={{marginTop:10}} class="stats">
                  <label>QuerySet:</label>
                  <select onChange={(event)=>{this.setState({"querysetIdx":event.target.value})}}>
                  {
                      this.state.stats.querysets.map((queryset, qidx)=>
                        (<option value={qidx}>{queryset.name}</option>)
                      )
                  }
                  </select>
                    <label>{"Total#:" + this.state.stats.querysets[this.state.querysetIdx].total}</label>
                    <label>{"Judged#:" + this.state.stats.querysets[this.state.querysetIdx].judged}</label>
                    <button class="button button2" onClick={()=>this.randomUrl(0)}>RandomUrl(Unjudged)</button>
                    <br/>
                    <input type="text" placeholder="sign your name.." ref="signature" onChange={()=>{this.updateStatistic()}} style={{"width":"100px", borderColor: ""}}/>
                    <label>{"Judged_By_You#:" + this.state.stats.querysets[this.state.querysetIdx].judgedByYou}</label>
                    <button onClick={()=>this.randomUrl(1)} class="button button2">RandomUrl(Judged)</button>
                </div>
            }
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
      judge:null,
      last_update:null
    }
    this.handleFormChange = this.handleFormChange.bind(this);
    this.handleUrlChange = this.handleUrlChange.bind(this);
    this.handleSaveJudge = this.handleSaveJudge.bind(this);
    this.handleLoadJudge = this.handleLoadJudge.bind(this);
    this.handleClearJudge = this.handleClearJudge.bind(this);
  }

  handleLoadJudge(event){
    if (this.state.url === ""){
        alert("Please: \n 1. Randome one judged url \n 2. Then submit this url") 
        return 
    }
    var json_d = {"url":this.state.url}
    axios.post(urlPrefix + "/load_judge", json_d, headers).then(
      (res) =>{
          if (res.data && res.data.textunits){
              this.setState({"textunits":res.data.textunits, 
                            "labels": res.data.labels             
            })
          }
      })
  }

  handleClearJudge(event){
    var json_d = {"url":this.state.url}
    axios.post(urlPrefix + "/clear_judge", json_d, headers).then(
      (res) =>{
          if (res.data.success)
          {
            this.setState({labels:null});
            alert("[Succeed] Clear the judge")
          }
          else{
            alert("[Failed] Please contact the dev.")
          }
          this.refs.form.updateStatistic()
      })
  }


  handleSaveJudge(event){
    if (this.state.url === ""){
        alert("Null Url") 
        return 
    }
      //var data = JSON.stringify(this.refs.textunits.textunits_labels);
      //verify the judge first 
      var judgeName = this.refs.form.refs.signature.value.trim()
      if (!judgeName){
        alert("[Failed] Please Sign Your Name First!")
        return
      }
      var json_d = {"url":this.state.url, "textunits":this.state.textunits, "labels":this.refs.textunits.labels, "judge":judgeName}
      axios.post(urlPrefix + "/save_judge", json_d, headers).then(
          (res) =>{
              res.data.success?
                  alert("[Succeed] with name " + judgeName + "."):
                  alert("[Failed] please contact the dev.")
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
        axios.post(urlPrefix + "/summary", data, headers)
            .then(
                res => {

                    this.setState({paragraphs: res.data.paragraphs,
                        textunits:res.data.textunits,
                        summary:res.data.summary,
                        url:url,
                        labels:res.data.labels,
                        judge:res.data.judge,
                        last_update:res.data.last_update
                    });
                }
            ).catch(err => {
                console.log(err);
            });
    }

    render() {
        return (
            <Grid>
            <Row>
            <h2 class='headline'> Deep Comparison</h2>
            <Form handleFormChange={this.handleFormChange} 
            handleUrlChange={this.handleUrlChange} 
            ref="form"
            />
        </Row>
        <Row>
          <Col md={4} lg={4}>
            <Paragraphs paragraphs={this.state.paragraphs}/>
          </Col>
          <Col md={4} lg={4}>
            <TextUnits textunits={this.state.textunits} 
                        url={this.state.url} 
                        labels={this.state.labels}
                        handleSaveJudge={this.handleSaveJudge}
                        handleLoadJudge={this.handleLoadJudge}
                        handleClearJudge={this.handleClearJudge}
                        judge={this.state.judge}
                        last_update={this.state.last_update}
                        ref="textunits"/>
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
