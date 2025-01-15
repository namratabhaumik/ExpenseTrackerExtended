import React, { useState, useEffect } from "react";
import Login from "./Login";
import axios from "axios";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [error, setError] = useState(null);

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    // Add any logout logic here if needed
  };

  return (
    <div className="App">
      <h1>Expense Tracker</h1>

      {!isAuthenticated ? (
        <Login onLoginSuccess={handleLoginSuccess} />
      ) : (
        <div>
          <p>Welcome! You are logged in.</p>
          <button onClick={handleLogout}>Logout</button>
          <h2>Upload Receipt</h2>
          {/* Placeholder for future receipt upload logic */}
        </div>
      )}
    </div>
  );
}

export default App;
