import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { FaTimes } from 'react-icons/fa';

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

export default ConfirmAccountModal;
