import React, { Component } from 'react';

function ParagraphDetail(props){
  const showHideDetail = (idx, isToShow) => {
       var pdid = "pd" + idx;
       var paragraph_details = document.getElementById(pdid);
       if(isToShow){
         paragraph_details.style.display = "block"
       }else{
         paragraph_details.style.display = "none"
       }
  }

  const detail = (p, idx) => (
      <div class='paragraph_detail' id={"pd" + idx}>
        <table>
          {
            Object.keys(p).map((attr) => {
                if (attr === "text" || attr === "text_nodes" 
                    || attr === "heading"
                    || attr === "xpath"
                    || attr === "sents"
                    ){
                      return null;
                }
                return <tr><td>{attr}</td><td>{p[attr].toString()}</td></tr>
            })
          }
        </table>
      </div>
  )
  return(
    props.p.is_boilerplate?
      <div>
        
        <p class="bad" style={{"display":props.show_boilerplate? "block":"none"}}
            onMouseOver={()=>showHideDetail(props.idx, true)}
            onMouseOut={()=>showHideDetail(props.idx, false)}
        >{props.p.text}</p>
        {detail(props.p, props.idx)}
      </div>
      : 
        <div>
          <p class="good"
            onMouseOver={()=>showHideDetail(props.idx, true)}
            onMouseOut={()=>showHideDetail(props.idx, false)}
          >{props.p.text}</p>
          {detail(props.p, props.idx)}
        </div> 
    ) 
}

class Paragraphs extends Component{
  constructor(props){
    super(props);
    this.props = props;
    this.state = {show:true}
  }

  render(){
    return (
          this.props.paragraphs == null?
          null:
          (
            <div class='column-results'>
              <input type="button" class="button button3"
                      value={this.state.show? "HideBoilerPlate" : "ShowBoilerPlate"} 
                      onClick={()=>{this.setState({'show': !this.state.show})}}/>
              {this.props.paragraphs.map((p, i) => 
                  <ParagraphDetail idx={i} p={p} show_boilerplate={this.state.show}/>
              )}
            </div>
          )
    )
  }
}
export default Paragraphs;