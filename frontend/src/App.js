import './App.css';
import React, { useState, useEffect } from "react";
import { Url } from './constants'



import Navbar from "./Navbar";

import {
  BrowserRouter as Router,
  Routes,
  Route,
} from "react-router-dom";

import Home from "./pages/home";
import Words from "./pages/words";
import Contact from "./pages/contact";

function App() {
  const [bg, setBg] = useState([]);
  useEffect(() => {
  }, []);

  return (
    <div className="App">
      <img src={bg} alt={"bg"} width={"100%"} className="img-bg" />
      <Router>
        <Navbar />
        <Routes>
          <Route exact path="/" element={<Home bg={bg} setBg={setBg}/>} />
          <Route path="/words" element={<Words bg={bg} setBg={setBg}/>} />
          <Route path="/contact" element={<Contact />}/>
        </Routes>
      </Router>

      <header className="App-header">
      </header>

    </div>
  );
}

export default App;
