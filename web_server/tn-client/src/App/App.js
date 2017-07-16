import React, { Component } from 'react';
import logo from './logo.png';

import NewsPanel from '../NewsPanel/NewsPanel';

import './App.css';
import 'materialize-css/dist/css/materialize.min.css';
import 'materialize-css/dist/js/materialize.min.js';

class App extends Component {
  render() {
    return (
      <div>
        <img className="logo" src={logo} alt="I am a logo" />
        <div>
          <NewsPanel />
        </div>
      </div>
    );
  }
}

export default App;