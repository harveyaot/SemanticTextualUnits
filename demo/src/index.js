import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import registerServiceWorker from './registerServiceWorker';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';

const WrappedApp = () =>(
	<MuiThemeProvider>
	<App/>
	</MuiThemeProvider>
	)
ReactDOM.render(
	<WrappedApp />, document.getElementById('root'));
registerServiceWorker();
