import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import PasswordPage from './PasswordPage';
import FileUpload from './FileUpload';
import './App.css';

function App() {
  const [isAuthenticated, setAuthenticated] = useState(false);

  return (
    <Router>
      <Routes>
        <Route path="/" element={isAuthenticated ? <FileUpload /> : <Navigate to="/login" />} />
        <Route path="/login" element={<PasswordPage setAuth={setAuthenticated} />} />
      </Routes>
    </Router>
  );
}

export default App;