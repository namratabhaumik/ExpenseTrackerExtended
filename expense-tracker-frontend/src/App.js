import React, { useState } from 'react';
import AuthForm from './Login';
import Expenses from './Expenses';
import './styles/App.css';

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
      {!isAuthenticated && <h1>Expense Tracker</h1>}
      {!isAuthenticated ? (
        <AuthForm onLoginSuccess={handleLoginSuccess} />
      ) : (
        <Expenses onLogout={handleLogout} accessToken={accessToken} />
      )}
    </div>
  );
}

export default App;
