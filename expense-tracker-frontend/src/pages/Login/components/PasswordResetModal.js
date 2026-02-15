import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { FaEye, FaEyeSlash, FaTimes } from 'react-icons/fa';

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

export default PasswordResetModal;
