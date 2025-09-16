import React from 'react';
import logo from './logo.svg';
import './App.css';
import ApiExample from './components/ApiExample';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <ApiExample />
      </header>
    </div>
  );
}

export default App;
