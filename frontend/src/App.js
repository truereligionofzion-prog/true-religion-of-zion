import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import MitzvotApp from "./components/MitzvotApp";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<MitzvotApp />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;