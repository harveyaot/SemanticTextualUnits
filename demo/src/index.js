import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import registerServiceWorker from './registerServiceWorker';

const WrappedApp = () =>(
	<App/>
	)
ReactDOM.render(
	<WrappedApp />, document.getElementById('root'));
registerServiceWorker();
