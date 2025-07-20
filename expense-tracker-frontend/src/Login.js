// Theme toggle is now global and handled by App.js. Do not add theme toggle UI here. See App.js for details.
import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { FaEye, FaEyeSlash } from 'react-icons/fa';
import { FaTimes } from 'react-icons/fa';
import './styles/Login.css';
import { ClipLoader } from 'react-spinners';

function ConfirmAccountModal({ open, email, onClose }) {
  const [code, setCode] = useState('');
  const [confirmError, setConfirmError] = useState('');
  const [confirmSuccess, setConfirmSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  if (!open) return null;

  const handleConfirm = async (e) => {
    e.preventDefault();
    setConfirmError('');
    setConfirmSuccess('');
    setLoading(true);
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/confirm-signup/`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, code }),
        },
      );
      const data = await response.json();
      if (response.ok) {
        setConfirmSuccess('Account verified! You can now log in.');
      } else {
        setConfirmError(data.error || data.message || 'Confirmation failed.');
      }
    } catch (err) {
      setConfirmError('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <button
          className="modal-close-x"
          onClick={onClose}
          aria-label="Close modal"
        >
          <FaTimes />
        </button>
        <h3>Confirm Your Account</h3>
        <p>
          Enter the code sent to <b>{email}</b>
        </p>
        <form onSubmit={handleConfirm} className="confirm-form">
          <input
            type="text"
            placeholder="Confirmation code"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            required
            maxLength={8}
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Verifying...' : 'Verify'}
          </button>
        </form>
        {confirmError && <p className="login-error">{confirmError}</p>}
        {confirmSuccess && <p className="signup-success">{confirmSuccess}</p>}
      </div>
    </div>
  );
}

ConfirmAccountModal.propTypes = {
  open: PropTypes.bool.isRequired,
  email: PropTypes.string.isRequired,
  onClose: PropTypes.func.isRequired,
};

function PasswordResetModal({ open, onClose }) {
  const [step, setStep] = useState(1); // 1: email, 2: code + new password
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  // Password requirements UI state
  const [passwordFocused, setPasswordFocused] = useState(false);

  // Validation helpers (same as signup form)
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
  const validatePassword = (pw) => passwordRules.every((rule) => rule.test(pw));
  const allPasswordRequirementsMet = validatePassword(newPassword);

  if (!open) return null;

  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/forgot-password/`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email }),
        },
      );
      const data = await response.json();
      if (response.ok) {
        setStep(2);
        setSuccess('Password reset code sent to your email.');
      } else {
        setError(data.error || data.message || 'Failed to send reset code.');
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordReset = async (e) => {
    e.preventDefault();
    setError('');
    if (!validatePassword(newPassword)) {
      setError('Password does not meet all requirements.');
      return;
    }
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    setLoading(true);
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/confirm-forgot-password/`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, code, new_password: newPassword }),
        },
      );
      const data = await response.json();
      if (response.ok) {
        setSuccess(
          'Password reset successful! You can now log in with your new password.',
        );
        // Close modal after 3 seconds
        setTimeout(() => {
          handleClose();
        }, 3000);
      } else {
        setError(data.error || data.message || 'Failed to reset password.');
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setStep(1);
    setEmail('');
    setCode('');
    setNewPassword('');
    setConfirmPassword('');
    setError('');
    setSuccess('');
    setLoading(false);
    setPasswordFocused(false);
    onClose();
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <button
          className="modal-close-x"
          onClick={handleClose}
          aria-label="Close modal"
        >
          <FaTimes />
        </button>
        <h3>Reset Password</h3>

        {step === 1 ? (
          <>
            <p>Enter your email address to receive a password reset code.</p>
            <form onSubmit={handleEmailSubmit} className="confirm-form">
              <input
                type="email"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <button type="submit" disabled={loading}>
                {loading ? 'Sending...' : 'Send Reset Code'}
              </button>
            </form>
          </>
        ) : (
          <>
            <p>
              Enter the code sent to <b>{email}</b> and your new password.
            </p>
            <form onSubmit={handlePasswordReset} className="confirm-form">
              <input
                type="text"
                placeholder="Reset code"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                required
                maxLength={8}
              />
              <div>
                <label htmlFor="reset-new-password">New Password:</label>
                <div className="password-input-wrapper">
                  <input
                    id="reset-new-password"
                    type={showNewPassword ? 'text' : 'password'}
                    placeholder="New password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    onFocus={() => setPasswordFocused(true)}
                    onBlur={() => setPasswordFocused(false)}
                    required
                    autoComplete="new-password"
                    style={{ paddingRight: '2.2rem' }}
                  />
                  <span
                    className="password-eye-icon"
                    onClick={() => setShowNewPassword((v) => !v)}
                    tabIndex={0}
                    role="button"
                    aria-label={
                      showNewPassword ? 'Hide password' : 'Show password'
                    }
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ')
                        setShowNewPassword((v) => !v);
                    }}
                  >
                    {showNewPassword ? <FaEyeSlash /> : <FaEye />}
                  </span>
                </div>
                {(passwordFocused || newPassword) &&
                  !allPasswordRequirementsMet && (
                  <ul className="password-requirements-list">
                    {passwordRules.map((rule) => {
                      const passed = rule.test(newPassword);
                      return (
                        <li
                          key={rule.message}
                          className={
                            passed ? 'requirement-met' : 'requirement-unmet'
                          }
                        >
                          <span className="requirement-icon">
                            {passed ? '✓' : '✗'}
                          </span>
                          {rule.message}
                        </li>
                      );
                    })}
                  </ul>
                )}
              </div>
              <div>
                <label htmlFor="reset-confirm-password">
                  Confirm New Password:
                </label>
                <div className="password-input-wrapper">
                  <input
                    id="reset-confirm-password"
                    type={showConfirmPassword ? 'text' : 'password'}
                    placeholder="Confirm new password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    autoComplete="new-password"
                    style={{ paddingRight: '2.2rem' }}
                  />
                  <span
                    className="password-eye-icon"
                    onClick={() => setShowConfirmPassword((v) => !v)}
                    tabIndex={0}
                    role="button"
                    aria-label={
                      showConfirmPassword ? 'Hide password' : 'Show password'
                    }
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ')
                        setShowConfirmPassword((v) => !v);
                    }}
                  >
                    {showConfirmPassword ? <FaEyeSlash /> : <FaEye />}
                  </span>
                </div>
                {confirmPassword && newPassword !== confirmPassword && (
                  <span className="input-error">Passwords do not match.</span>
                )}
              </div>
              <button type="submit" disabled={loading}>
                {loading ? 'Resetting...' : 'Reset Password'}
              </button>
            </form>
          </>
        )}

        {error && <p className="login-error">{error}</p>}
        {success && <p className="signup-success">{success}</p>}
      </div>
    </div>
  );
}

PasswordResetModal.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
};

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
  // Password reset modal state
  const [showPasswordResetModal, setShowPasswordResetModal] = useState(false);
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
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/login/`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: loginEmail, password: loginPassword }),
        },
      );
      if (response.ok) {
        const result = await response.json();
        onLoginSuccess(result.access_token);
      } else {
        const errorData = await response.json();
        setLoginError(errorData.message || 'Login failed. Please try again.');
      }
    } catch (err) {
      setLoginError('An error occurred. Please try again later.');
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
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/signup/`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: signupEmail,
            password: signupPassword,
          }),
        },
      );
      if (response.ok) {
        setSignupSuccess(
          'Sign up successful! Please check your email to verify your account.',
        );
        setSignupEmail('');
        setSignupPassword('');
        setSignupConfirm('');
        setConfirmEmail(signupEmail);
        setShowConfirmModal(true);
      } else {
        const errorData = await response.json();
        setSignupError(
          errorData.error ||
            errorData.message ||
            'Sign up failed. Please try again.',
        );
      }
    } catch (err) {
      setSignupError('An error occurred. Please try again later.');
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
              <span
                className="auth-link forgot-password"
                onClick={() => setShowPasswordResetModal(true)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ')
                    setShowPasswordResetModal(true);
                }}
              >
                Forgot Password?
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
                            {passed ? '✓' : '✗'}
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
        <PasswordResetModal
          open={showPasswordResetModal}
          onClose={() => setShowPasswordResetModal(false)}
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
