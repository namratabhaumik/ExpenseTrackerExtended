import React, { useState } from 'react';
import AuthForm from './pages/Login/Login';
import Expenses from './pages/Expenses/Expenses';
import Dashboard from './pages/Dashboard/Dashboard';
import Categories from './pages/Categories/Categories';
import Profile from './pages/Profile/Profile';
import Navbar from './components/Navbar/Navbar';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [activePage, setActivePage] = useState('dashboard');
  const [theme, setTheme] = useState(() => {
    // Get theme from localStorage or default to light
    if (typeof window !== 'undefined') {
      return localStorage.getItem('theme') || 'light';
    }
    return 'light';
  });
  const [dashboardRefreshFlag, setDashboardRefreshFlag] = useState(0);

  // Apply theme to body
  React.useEffect(() => {
    if (typeof window !== 'undefined') {
      document.body.classList.toggle('dark', theme === 'dark');
      localStorage.setItem('theme', theme);
    }
  }, [theme]);

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
    setActivePage('dashboard');
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setActivePage('dashboard');
  };

  const handleThemeToggle = () => {
    setTheme((prevTheme) => (prevTheme === 'dark' ? 'light' : 'dark'));
  };

  return (
    <div className={`min-h-screen ${theme === 'dark' ? 'dark' : ''}`}>
      {!isAuthenticated && (
        <button
          onClick={handleThemeToggle}
          aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          className="global-theme-toggle-btn"
          type="button"
          style={{
            position: 'fixed',
            top: 24,
            right: 24,
            zIndex: 100,
            background: 'rgba(249,250,251,0.95)',
            color: theme === 'dark' ? '#F9FAFB' : '#4B5563',
            border: '1px solid #9CA3AF',
            borderRadius: 8,
            padding: '0.5rem 0.75rem',
            fontSize: 20,
            boxShadow: '0 2px 8px rgba(75,85,99,0.08)',
            transition: 'all 0.2s',
          }}
        >
          {theme === 'dark' ? '' : ''}
        </button>
      )}
      {isAuthenticated && (
        <Navbar
          onLogout={handleLogout}
          onNavigate={setActivePage}
          activePage={activePage}
          theme={theme}
          onThemeToggle={handleThemeToggle}
        />
      )}
      {!isAuthenticated ? (
        <AuthForm onLoginSuccess={handleLoginSuccess} theme={theme} />
      ) : (
        <main className="app-container">
          {activePage === 'dashboard' && (
            <div className="content-wrapper">
              <Dashboard refreshFlag={dashboardRefreshFlag} />
            </div>
          )}
          {activePage === 'expenses' && (
            <div className="content-wrapper">
              <Expenses setDashboardRefreshFlag={setDashboardRefreshFlag} />
            </div>
          )}
          {activePage === 'categories' && (
            <div className="content-wrapper">
              <Categories onNavigate={setActivePage} />
            </div>
          )}
          {activePage === 'profile' && (
            <div className="content-wrapper">
              <Profile theme={theme} />
            </div>
          )}
        </main>
      )}
    </div>
  );
}

export default App;
