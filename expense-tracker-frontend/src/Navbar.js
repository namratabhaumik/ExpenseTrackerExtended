import React, { useState } from 'react';
import PropTypes from 'prop-types';
import './styles/Navbar.css';

const NAV_LINKS = [
  { label: 'Dashboard', page: 'dashboard' },
  { label: 'Expenses', page: 'expenses' },
  { label: 'Categories', page: 'categories' },
];
const USER_LINKS = [{ label: 'Profile', page: 'profile' }];

export default function Navbar({
  onLogout,
  onNavigate,
  activePage,
  theme,
  onThemeToggle,
  // New: fallback prop for demo/testing
  fallback = false,
}) {
  const [menuOpen, setMenuOpen] = useState(false);

  const handleKeyDown = (e, action) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      action();
    }
  };

  // Fallback nav for unauthenticated/demo mode
  if (fallback) {
    return (
      <nav className="sticky top-0 z-40 bg-[#4B5563] text-[#F9FAFB] shadow-lg">
        <div className="max-w-7xl mx-auto flex items-center justify-between py-4 px-6">
          <div className="flex items-center gap-x-6">
            <span className="text-xl font-bold tracking-tight">
              ExpenseTrackerExtended
            </span>
            <div className="flex gap-x-4">
              {NAV_LINKS.map((link) => (
                <button
                  key={link.page}
                  className="nav-link relative font-medium hover:text-[#2563EB] transition-all duration-200 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-[#2563EB] focus:ring-offset-2 focus:ring-offset-[#4B5563] rounded-md px-3 py-2"
                  aria-label={`Navigate to ${link.label}`}
                  style={{ minWidth: 110 }}
                >
                  {link.label}
                </button>
              ))}
              {USER_LINKS.map((link) => (
                <button
                  key={link.page}
                  className="nav-link relative font-medium hover:text-[#2563EB] transition-all duration-200 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-[#2563EB] focus:ring-offset-2 focus:ring-offset-[#4B5563] rounded-md px-3 py-2"
                  aria-label={`Navigate to ${link.label}`}
                  style={{ minWidth: 110 }}
                >
                  {link.label}
                </button>
              ))}
              <button
                className="nav-link font-medium hover:text-[#2563EB] transition-all duration-200 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-[#2563EB] focus:ring-offset-2 focus:ring-offset-[#4B5563] rounded-md px-3 py-2"
                aria-label="Logout"
                style={{ minWidth: 110 }}
              >
                Logout
              </button>
            </div>
          </div>
          <button
            onClick={onThemeToggle}
            className="theme-toggle p-2 rounded-md hover:bg-[#6B7280] transition-all duration-200 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-[#2563EB] focus:ring-offset-2 focus:ring-offset-[#4B5563]"
            aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
        </div>
      </nav>
    );
  }

  return (
    <nav className="sticky top-0 z-40 bg-[#4B5563] text-[#F9FAFB] shadow-lg">
      <div className="max-w-7xl mx-auto flex items-center justify-between py-4 px-6">
        {/* Left: Brand and Nav */}
        <div className="flex items-center gap-x-6">
          <button
            className="text-xl font-bold tracking-tight hover:text-[#2563EB] transition-all duration-200 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-[#2563EB] focus:ring-offset-2 focus:ring-offset-[#4B5563] rounded-md"
            onClick={() => onNavigate('dashboard')}
            onKeyDown={(e) => handleKeyDown(e, () => onNavigate('dashboard'))}
            aria-current={activePage === 'dashboard' ? 'page' : undefined}
            aria-label="Navigate to Dashboard"
          >
            ExpenseTrackerExtended
          </button>
          <div className="hidden md:flex gap-x-4">
            {NAV_LINKS.map((link) => (
              <button
                key={link.page}
                onClick={() => onNavigate(link.page)}
                onKeyDown={(e) => handleKeyDown(e, () => onNavigate(link.page))}
                className={`nav-link relative font-medium hover:text-[#2563EB] transition-all duration-200 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-[#2563EB] focus:ring-offset-2 focus:ring-offset-[#4B5563] rounded-md px-3 py-2${
                  activePage === link.page ? ' active' : ''
                }`}
                aria-current={activePage === link.page ? 'page' : undefined}
                aria-label={`Navigate to ${link.label}`}
              >
                {link.label}
              </button>
            ))}
          </div>
        </div>
        {/* Right: User Actions and Theme Toggle */}
        <div className="hidden md:flex items-center gap-x-4">
          {USER_LINKS.map((link) => (
            <button
              key={link.page}
              onClick={() => onNavigate(link.page)}
              onKeyDown={(e) => handleKeyDown(e, () => onNavigate(link.page))}
              className={`nav-link relative font-medium hover:text-[#2563EB] transition-all duration-200 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-[#2563EB] focus:ring-offset-2 focus:ring-offset-[#4B5563] rounded-md px-3 py-2${
                activePage === link.page ? ' active' : ''
              }`}
              aria-current={activePage === link.page ? 'page' : undefined}
              aria-label={`Navigate to ${link.label}`}
            >
              {link.label}
            </button>
          ))}
          <button
            onClick={onLogout}
            onKeyDown={(e) => handleKeyDown(e, onLogout)}
            className="nav-link font-medium hover:text-[#2563EB] transition-all duration-200 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-[#2563EB] focus:ring-offset-2 focus:ring-offset-[#4B5563] rounded-md px-3 py-2"
            aria-label="Logout"
          >
            Logout
          </button>
          {/* Dark Mode Toggle */}
          <button
            onClick={onThemeToggle}
            onKeyDown={(e) => handleKeyDown(e, onThemeToggle)}
            className="theme-toggle p-2 rounded-md hover:bg-[#5EEAD4] transition-all duration-200 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-[#14B8A6] focus:ring-offset-2 focus:ring-offset-[#23272F]"
            aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            {theme === 'dark' ? (
              <svg className="w-5 h-5" fill="#10B981" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z"
                  clipRule="evenodd"
                />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="#14B8A6" viewBox="0 0 20 20">
                <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
              </svg>
            )}
          </button>
        </div>
        {/* Hamburger (Mobile) */}
        <button
          className="md:hidden flex flex-col justify-center items-center w-10 h-10 hover:scale-105 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-[#2563EB] focus:ring-offset-2 focus:ring-offset-[#4B5563] rounded-md"
          aria-label="Open menu"
          aria-expanded={menuOpen}
          aria-controls="mobile-menu"
          onClick={() => setMenuOpen(true)}
          onKeyDown={(e) => handleKeyDown(e, () => setMenuOpen(true))}
        >
          <span className="block w-6 h-0.5 bg-[#F9FAFB] mb-1 transition-all duration-200"></span>
          <span className="block w-6 h-0.5 bg-[#F9FAFB] mb-1 transition-all duration-200"></span>
          <span className="block w-6 h-0.5 bg-[#F9FAFB] transition-all duration-200"></span>
        </button>
      </div>
      {/* Mobile Menu Overlay */}
      {menuOpen && (
        <div
          className="mobile-menu-overlay fixed inset-0 z-50 bg-[#4B5563] bg-opacity-95 flex flex-col"
          id="mobile-menu"
          role="dialog"
          aria-modal="true"
          aria-label="Navigation menu"
        >
          <div className="flex items-center justify-between px-6 py-4">
            <button
              className="text-xl font-bold tracking-tight hover:text-[#2563EB] transition-all duration-200 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-[#2563EB] focus:ring-offset-2 focus:ring-offset-[#4B5563] rounded-md"
              onClick={() => {
                onNavigate('dashboard');
                setMenuOpen(false);
              }}
              onKeyDown={(e) =>
                handleKeyDown(e, () => {
                  onNavigate('dashboard');
                  setMenuOpen(false);
                })
              }
              aria-current={activePage === 'dashboard' ? 'page' : undefined}
              aria-label="Navigate to Dashboard"
            >
              ExpenseTrackerExtended
            </button>
            <div className="flex items-center gap-x-2">
              {/* Mobile Theme Toggle */}
              <button
                onClick={onThemeToggle}
                onKeyDown={(e) => handleKeyDown(e, onThemeToggle)}
                className="theme-toggle p-2 rounded-md hover:bg-[#6B7280] transition-all duration-200 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-[#2563EB] focus:ring-offset-2 focus:ring-offset-[#4B5563]"
                aria-label={`Switch to ${
                  theme === 'dark' ? 'light' : 'dark'
                } mode`}
              >
                {theme === 'dark' ? (
                  <svg
                    className="w-5 h-5"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z"
                      clipRule="evenodd"
                    />
                  </svg>
                ) : (
                  <svg
                    className="w-5 h-5"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                  </svg>
                )}
              </button>
              <button
                className="text-3xl text-[#F9FAFB] hover:text-[#2563EB] transition-all duration-200 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-[#2563EB] focus:ring-offset-2 focus:ring-offset-[#4B5563] rounded-md w-10 h-10 flex items-center justify-center"
                aria-label="Close menu"
                onClick={() => setMenuOpen(false)}
                onKeyDown={(e) => handleKeyDown(e, () => setMenuOpen(false))}
              >
                &times;
              </button>
            </div>
          </div>
          <div className="flex flex-col gap-y-6 px-8 mt-8">
            {NAV_LINKS.map((link) => (
              <button
                key={link.page}
                onClick={() => {
                  onNavigate(link.page);
                  setMenuOpen(false);
                }}
                onKeyDown={(e) =>
                  handleKeyDown(e, () => {
                    onNavigate(link.page);
                    setMenuOpen(false);
                  })
                }
                className={`mobile-nav-link text-lg font-medium hover:text-[#2563EB] transition-all duration-200 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-[#2563EB] focus:ring-offset-2 focus:ring-offset-[#4B5563] rounded-md px-3 py-2 text-left${
                  activePage === link.page ? ' active' : ''
                }`}
                aria-current={activePage === link.page ? 'page' : undefined}
                aria-label={`Navigate to ${link.label}`}
              >
                {link.label}
              </button>
            ))}
            <div className="border-t border-[#9CA3AF] my-4"></div>
            {USER_LINKS.map((link) => (
              <button
                key={link.page}
                onClick={() => {
                  onNavigate(link.page);
                  setMenuOpen(false);
                }}
                onKeyDown={(e) =>
                  handleKeyDown(e, () => {
                    onNavigate(link.page);
                    setMenuOpen(false);
                  })
                }
                className={`mobile-nav-link text-lg font-medium hover:text-[#2563EB] transition-all duration-200 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-[#2563EB] focus:ring-offset-2 focus:ring-offset-[#4B5563] rounded-md px-3 py-2 text-left${
                  activePage === link.page ? ' active' : ''
                }`}
                aria-current={activePage === link.page ? 'page' : undefined}
                aria-label={`Navigate to ${link.label}`}
              >
                {link.label}
              </button>
            ))}
            <button
              onClick={() => {
                setMenuOpen(false);
                onLogout && onLogout();
              }}
              onKeyDown={(e) =>
                handleKeyDown(e, () => {
                  setMenuOpen(false);
                  onLogout && onLogout();
                })
              }
              className="mobile-nav-link text-lg font-medium hover:text-[#2563EB] transition-all duration-200 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-[#2563EB] focus:ring-offset-2 focus:ring-offset-[#4B5563] rounded-md px-3 py-2 text-left"
              aria-label="Logout"
            >
              Logout
            </button>
          </div>
        </div>
      )}
    </nav>
  );
}

Navbar.propTypes = {
  onLogout: PropTypes.func.isRequired,
  onNavigate: PropTypes.func.isRequired,
  activePage: PropTypes.string.isRequired,
  theme: PropTypes.string.isRequired,
  onThemeToggle: PropTypes.func.isRequired,
  // New: fallback prop for demo/testing
  fallback: PropTypes.bool,
};
