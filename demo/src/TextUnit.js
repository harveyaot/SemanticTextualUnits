import React, { Component } from 'react';

class SentSpan extends Component{

    constructor(props){
        super(props);
        if (typeof props.labels
            && props.labels[props.tidx]
            && props.labels[props.tidx].ps[props.pidx]
            && props.labels[props.tidx].ps[props.pidx][props.sidx]){
            this.state = {selected:true}
        }else{
            this.state={selected: false }
        }
        this.handleClick = this.handleClick.bind(this)
    }

    handleClick(){
        this.setState({'selected': !this.state.selected})
        this.props.handleLabel(!this.state.selected,
            this.props.tidx,
            this.props.pidx,
            this.props.sidx
        )
    }

    render(){
        return (
            <span class="sent"
            onClick={this.handleClick} 
            ref="span"
            style={{"backgroundColor":this.state.selected? 'yellow':null}}
            >
            {this.props.sent + " "}
            </span>
        )
    }
}
class TextUnit extends Component{
    // represent single textunit 
    constructor(props){
        super(props);
        if (props.labels 
            && props.labels[props.tidx]
            && props.labels[props.tidx].label){
            this.state={checked: true}
        }else{
            this.state = {checked: false};
        }
        this.handleCheck = this.handleCheck.bind(this);
    }

    handleCheck(event){
        this.setState({checked: event.target.checked})
        this.props.handleLabel(event.target.checked, this.props.tidx, null, null)
    }
    
    render(){
        return (
            <div class="textunit" id={"tu" + this.props.tidx}>
            <div style={{backgroundColor:this.state.checked? '#4192f4': null}}>
                  <b>{this.props.textunit.topic_paragraph.text}</b>
                  <input type='checkbox'
                   checked={this.state.checked}
                   onChange={this.handleCheck}
                  />
                  {
                    this.props.textunit.paragraphs.map((p,pidx) =>
                        (<p>
                            {
                                p.sents.map((sent,sidx) =>
                                  <SentSpan sent={sent} tidx={this.props.tidx} pidx={pidx} sidx={sidx} 
                                  handleLabel={this.props.handleLabel} labels={this.props.labels}/>
                                )
                            }
                        </p>)
                    )
                  } 
            </div>
            </div>
        )
    }
}

class TextUnits extends Component{
    constructor(props){
        super(props)
        this.props = props
        this.labels = []
        this.handleLabel=this.handleLabel.bind(this)
    }

    handleLabel(label, tidx, pidx, sidx){
        if (typeof this.labels[tidx] === 'undefined'
            || this.labels[tidx] === null){
            this.labels[tidx] = {'label':null, 'ps':[]}
        }
        if (pidx === null && sidx === null){
            this.labels[tidx].label = label
        }
        else{
            if (typeof this.labels[tidx].ps[pidx] === 'undefined'
                || this.labels[tidx].ps[pidx] === null){
                this.labels[tidx].ps[pidx] = [] 
            } 
            this.labels[tidx].ps[pidx][sidx] = label
            }
    }

    render(){
        this.labels = this.props.labels
        if (this.labels === null){
            this.labels = []
        }
        return (
            this.props.textunits === null?
            null:
            <div class="column-results">
                  <input type="button" class="button button3" value="SaveJudge" onClick={this.props.handleSaveJudge}/>
                  <input type="button" class="button button3" value="ClearJudge" onClick={this.props.handleClearJudge}/>
                  <label class='note'>{this.props.last_update? this.props.judge + "@" + new Date(this.props.last_update.$date).toUTCString():null}</label>

                {this.props.textunits.map((tu, tidx) => (
                    <TextUnit key={this.props.url + "_" + Math.random() + "_"+ tidx}  textunit={tu} tidx={tidx} handleLabel={this.handleLabel} labels={this.labels}/> 
                ))}
            </div>
        )
    }
}

export default TextUnits;
