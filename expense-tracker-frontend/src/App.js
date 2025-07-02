import React, { useState } from 'react';
import Login from './Login';
import Expenses from './Expenses';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [accessToken, setAccessToken] = useState('');

  const handleLoginSuccess = (token) => {
    setIsAuthenticated(true);
    setAccessToken(token);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setAccessToken('');
  };

  return (
    <div className="App">
      <h1>Expense Tracker</h1>

      {!isAuthenticated ? (
        <Login onLoginSuccess={handleLoginSuccess} />
      ) : (
        <Expenses onLogout={handleLogout} accessToken={accessToken} />
      )}
    </div>
  );
}

export default App;
