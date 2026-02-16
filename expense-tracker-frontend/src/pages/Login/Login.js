import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { FaEye, FaEyeSlash } from 'react-icons/fa';
import { ClipLoader } from 'react-spinners';
import './Login.css';
import ConfirmAccountModal from './components/ConfirmAccountModal';
import { apiPost, APIError, clearCSRFTokenCache } from '../../services/api';

function AuthForm({ onLoginSuccess, theme }) {
  const [activeTab, setActiveTab] = useState('login');
  // Login state
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  const [loginLoading, setLoginLoading] = useState(false);
  // Sign Up state
  const [signupEmail, setSignupEmail] = useState('');
  const [signupPassword, setSignupPassword] = useState('');
  const [signupConfirm, setSignupConfirm] = useState('');
  const [signupError, setSignupError] = useState('');
  const [signupSuccess, setSignupSuccess] = useState('');
  const [signupLoading, setSignupLoading] = useState(false);
  // Password visibility
  const [showLoginPassword, setShowLoginPassword] = useState(false);
  const [showSignupPassword, setShowSignupPassword] = useState(false);
  const [showSignupConfirm, setShowSignupConfirm] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [confirmEmail, setConfirmEmail] = useState('');
  // Password requirements UI state
  const [passwordFocused, setPasswordFocused] = useState(false);

  // Validation helpers
  const passwordRules = [
    {
      test: (pw) => pw.length >= 8,
      message: 'At least 8 characters',
    },
    {
      test: (pw) => /[A-Z]/.test(pw),
      message: 'At least one uppercase letter',
    },
    {
      test: (pw) => /[a-z]/.test(pw),
      message: 'At least one lowercase letter',
    },
    {
      test: (pw) => /[0-9]/.test(pw),
      message: 'At least one number',
    },
    {
      test: (pw) => /[^A-Za-z0-9]/.test(pw),
      message: 'At least one special character',
    },
  ];
  const validateEmail = (email) => /.+@.+\..+/.test(email);
  const validatePassword = (pw) => passwordRules.every((rule) => rule.test(pw));

  // Login handler
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError('');
    setLoginLoading(true);
    try {
      await apiPost('/api/login/', {
        email: loginEmail,
        password: loginPassword,
      });
      // Clear cached CSRF token since Django rotates it after login
      clearCSRFTokenCache();
      onLoginSuccess();
    } catch (err) {
      if (err instanceof APIError) {
        setLoginError(err.message || 'Login failed. Please try again.');
      } else {
        setLoginError('An error occurred. Please try again later.');
      }
    } finally {
      setLoginLoading(false);
    }
  };

  // Sign Up handler
  const handleSignup = async (e) => {
    e.preventDefault();
    setSignupError('');
    setSignupSuccess('');
    if (!validateEmail(signupEmail)) {
      setSignupError('Invalid email format.');
      return;
    }
    if (!validatePassword(signupPassword)) {
      setSignupError('Password does not meet all requirements.');
      return;
    }
    if (signupPassword !== signupConfirm) {
      setSignupError('Passwords do not match.');
      return;
    }
    setSignupLoading(true);
    try {
      await apiPost('/api/signup/', {
        email: signupEmail,
        password: signupPassword,
      });
      setSignupSuccess(
        'Sign up successful! You can now log in with your credentials.',
      );
      setSignupEmail('');
      setSignupPassword('');
      setSignupConfirm('');
    } catch (err) {
      if (err instanceof APIError) {
        setSignupError(
          err.message || 'Sign up failed. Please try again.',
        );
      } else {
        setSignupError('An error occurred. Please try again later.');
      }
    } finally {
      setSignupLoading(false);
    }
  };

  const allPasswordRequirementsMet = validatePassword(signupPassword);

  // Theme toggle handler
  // Removed theme toggle handler
  // Apply theme to body
  React.useEffect(() => {
    if (typeof window !== 'undefined') {
      document.body.classList.toggle('dark', theme === 'dark');
    }
  }, [theme]);

  return (
    <div>
      {/* Removed theme-toggle-container and button */}
      <div
        className={`login-container ${theme === 'dark' ? 'dark' : ''}`}
        data-testid="login-container"
      >
        <div className="auth-tabs">
          <button
            className={`auth-tab${activeTab === 'login' ? ' active' : ''}`}
            onClick={() => setActiveTab('login')}
            aria-selected={activeTab === 'login'}
            tabIndex={activeTab === 'login' ? 0 : -1}
          >
            Login
          </button>
          <button
            className={`auth-tab${activeTab === 'signup' ? ' active' : ''}`}
            onClick={() => setActiveTab('signup')}
            aria-selected={activeTab === 'signup'}
            tabIndex={activeTab === 'signup' ? 0 : -1}
          >
            Sign Up
          </button>
        </div>
        {activeTab === 'login' ? (
          <>
            <form
              className="login-form"
              onSubmit={handleLogin}
              autoComplete="on"
            >
              <div>
                <label htmlFor="login-email">Email:</label>
                <div className="password-input-wrapper">
                  <input
                    id="login-email"
                    type="email"
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    required
                    autoComplete="username"
                    placeholder="john.doe@example.com"
                    className="focus:border-[#2563EB] focus:ring-2 focus:ring-[#2563EB] dark:bg-[#23272F] dark:text-[#F3F4F6] dark:placeholder-[#9CA3AF]"
                    aria-label="Email"
                  />
                </div>
              </div>
              <div>
                <label htmlFor="login-password">Password:</label>
                <div className="password-input-wrapper">
                  <input
                    id="login-password"
                    type={showLoginPassword ? 'text' : 'password'}
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    required
                    autoComplete="current-password"
                    placeholder="password"
                    style={{ paddingRight: '2.2rem' }}
                    className="focus:border-[#2563EB] focus:ring-2 focus:ring-[#2563EB] dark:bg-[#23272F] dark:text-[#F3F4F6] dark:placeholder-[#9CA3AF]"
                    aria-label="Password"
                  />
                  <span
                    className="password-eye-icon"
                    onClick={() => setShowLoginPassword((v) => !v)}
                    tabIndex={0}
                    role="button"
                    aria-label={
                      showLoginPassword ? 'Hide password' : 'Show password'
                    }
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ')
                        setShowLoginPassword((v) => !v);
                    }}
                  >
                    {showLoginPassword ? <FaEyeSlash /> : <FaEye />}
                  </span>
                </div>
              </div>
              <button
                type="submit"
                disabled={loginLoading}
                className="flex items-center justify-center gap-2"
              >
                {loginLoading ? <ClipLoader size={20} color="#fff" /> : 'Login'}
              </button>
            </form>
            <div className="auth-links center-auth-link">
              <span
                className="auth-link"
                onClick={() => setActiveTab('signup')}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ')
                    setActiveTab('signup');
                }}
              >
                Don&apos;t have an account? Sign Up
              </span>
            </div>
            {loginError && <p className="login-error">{loginError}</p>}
          </>
        ) : (
          <>
            <form
              className="login-form"
              onSubmit={handleSignup}
              autoComplete="on"
            >
              <div>
                <label htmlFor="signup-email">Email:</label>
                <div className="password-input-wrapper">
                  <input
                    id="signup-email"
                    type="email"
                    value={signupEmail}
                    onChange={(e) => setSignupEmail(e.target.value)}
                    required
                    autoComplete="username"
                    placeholder="john.doe@example.com"
                    className="focus:border-[#2563EB] focus:ring-2 focus:ring-[#2563EB] dark:bg-[#23272F] dark:text-[#F3F4F6] dark:placeholder-[#9CA3AF]"
                    aria-label="Email"
                  />
                </div>
                {signupEmail && !validateEmail(signupEmail) && (
                  <span className="input-error">Invalid email format.</span>
                )}
              </div>
              <div>
                <label htmlFor="signup-password">Password:</label>
                <div className="password-input-wrapper">
                  <input
                    id="signup-password"
                    type={showSignupPassword ? 'text' : 'password'}
                    value={signupPassword}
                    onChange={(e) => setSignupPassword(e.target.value)}
                    onFocus={() => setPasswordFocused(true)}
                    onBlur={() => setPasswordFocused(false)}
                    required
                    autoComplete="new-password"
                    placeholder="password"
                    style={{ paddingRight: '2.2rem' }}
                    className="focus:border-[#2563EB] focus:ring-2 focus:ring-[#2563EB] dark:bg-[#23272F] dark:text-[#F3F4F6] dark:placeholder-[#9CA3AF]"
                    aria-label="Password"
                  />
                  <span
                    className="password-eye-icon"
                    onClick={() => setShowSignupPassword((v) => !v)}
                    tabIndex={0}
                    role="button"
                    aria-label={
                      showSignupPassword ? 'Hide password' : 'Show password'
                    }
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ')
                        setShowSignupPassword((v) => !v);
                    }}
                  >
                    {showSignupPassword ? <FaEyeSlash /> : <FaEye />}
                  </span>
                </div>
                {(passwordFocused || signupPassword) &&
                  !allPasswordRequirementsMet && (
                  <ul className="password-requirements-list">
                    {passwordRules.map((rule) => {
                      const passed = rule.test(signupPassword);
                      return (
                        <li
                          key={rule.message}
                          className={
                            passed ? 'requirement-met' : 'requirement-unmet'
                          }
                        >
                          <span className="requirement-icon">
                            {passed ? '' : ''}
                          </span>
                          {rule.message}
                        </li>
                      );
                    })}
                  </ul>
                )}
              </div>
              <div>
                <label htmlFor="signup-confirm">Confirm Password:</label>
                <div className="password-input-wrapper">
                  <input
                    id="signup-confirm"
                    type={showSignupConfirm ? 'text' : 'password'}
                    value={signupConfirm}
                    onChange={(e) => setSignupConfirm(e.target.value)}
                    required
                    autoComplete="new-password"
                    placeholder="password"
                    style={{ paddingRight: '2.2rem' }}
                    className="focus:border-[#2563EB] focus:ring-2 focus:ring-[#2563EB] dark:bg-[#23272F] dark:text-[#F3F4F6] dark:placeholder-[#9CA3AF]"
                    aria-label="Confirm Password"
                  />
                  <span
                    className="password-eye-icon"
                    onClick={() => setShowSignupConfirm((v) => !v)}
                    tabIndex={0}
                    role="button"
                    aria-label={
                      showSignupConfirm ? 'Hide password' : 'Show password'
                    }
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ')
                        setShowSignupConfirm((v) => !v);
                    }}
                  >
                    {showSignupConfirm ? <FaEyeSlash /> : <FaEye />}
                  </span>
                </div>
                {signupConfirm && signupPassword !== signupConfirm && (
                  <span className="input-error">Passwords do not match.</span>
                )}
              </div>
              <button
                type="submit"
                disabled={signupLoading}
                className="flex items-center justify-center gap-2"
              >
                {signupLoading ? (
                  <ClipLoader size={20} color="#fff" />
                ) : (
                  'Sign Up'
                )}
              </button>
            </form>
            <div className="auth-links center-auth-link">
              <span
                className="auth-link"
                onClick={() => setActiveTab('login')}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') setActiveTab('login');
                }}
              >
                Already have an account? Login
              </span>
            </div>
            {signupError && <p className="login-error">{signupError}</p>}
            {signupSuccess && <p className="signup-success">{signupSuccess}</p>}
          </>
        )}
        <ConfirmAccountModal
          open={showConfirmModal}
          email={confirmEmail}
          onClose={() => {
            setShowConfirmModal(false);
            setActiveTab('login');
          }}
        />
      </div>
    </div>
  );
}

AuthForm.propTypes = {
  onLoginSuccess: PropTypes.func.isRequired,
  theme: PropTypes.string.isRequired,
};

export default AuthForm;
