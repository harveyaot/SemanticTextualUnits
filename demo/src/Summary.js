import React, { Component } from 'react';

class Summary extends Component{
  constructor(props){
    super(props)
    this.props = props  
  }
  render(){
    return (
          this.props.summary == null?
          null:
          (
            <div class='summary column-results'>
                <p class='summary'>
                  <b>{this.props.summary.title}</b>
                </p>

                <ol type="1">
                {this.props.summary.subtopics.map((s) =>(
                  <li>{s.topic}<br/>
                    <span class='key_difference'>{s.content}</span>
                  </li>
                ))}
                </ol>
            </div>
          )
    )
  }
}

export default Summary;