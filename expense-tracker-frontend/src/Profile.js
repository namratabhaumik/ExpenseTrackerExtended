import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './styles/Profile.css';
import { FaEye, FaEyeSlash } from 'react-icons/fa';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

function Profile({ accessToken, theme }) {
  // State for profile info
  const [profile, setProfile] = useState({ name: '', email: '' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editMode, setEditMode] = useState(false);
  const [editProfile, setEditProfile] = useState({ name: '', email: '' });
  const [saveLoading, setSaveLoading] = useState(false);

  // State for password change
  const [pwForm, setPwForm] = useState({ current: '', new1: '', new2: '' });
  const [pwLoading, setPwLoading] = useState(false);
  const [pwFocused, setPwFocused] = useState(false);
  const [pwError, setPwError] = useState('');

  // Show/hide password state
  const [showPw, setShowPw] = useState({
    current: false,
    new1: false,
    new2: false,
  });
  // Add aria-live region for feedback
  const [ariaMessage, setAriaMessage] = useState('');

  // Password validation rules
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
  const allPasswordRequirementsMet = validatePassword(pwForm.new1);

  // Fetch profile info on mount
  useEffect(() => {
    if (!accessToken) return;
    setLoading(true);
    setError('');
    fetch(`${API_BASE}/api/profile/`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    })
      .then(async (resp) => {
        if (!resp.ok) {
          const err = await resp.json();
          throw new Error(err.error || 'Failed to fetch profile');
        }
        return resp.json();
      })
      .then((data) => {
        setProfile({
          name: data.profile.name || '',
          email: data.profile.email || '',
        });
        setEditProfile({
          name: data.profile.name || '',
          email: data.profile.email || '',
        });
      })
      .catch((e) => setError(e.message || 'An error occurred.'))
      .finally(() => setLoading(false));
  }, [accessToken]);

  // Handle profile form input
  const handleEditChange = (e) => {
    setEditProfile({ ...editProfile, [e.target.name]: e.target.value });
  };

  // Validate email format
  const validateEmail = (email) => /.+@.+\..+/.test(email);

  // Save profile changes
  const handleSaveProfile = async (e) => {
    e.preventDefault();
    if (!validateEmail(editProfile.email)) {
      toast.error('Invalid email format.', toastOptions('error'));
      return;
    }
    setSaveLoading(true);
    try {
      const resp = await fetch(`${API_BASE}/api/profile/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          name: editProfile.name,
          email: editProfile.email,
        }),
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || 'Failed to update profile');
      setProfile({ ...editProfile });
      setEditMode(false);
      toast.success('Profile updated successfully!', toastOptions('success'));
    } catch (e) {
      toast.error(
        e.message || 'Failed to update profile.',
        toastOptions('error'),
      );
    } finally {
      setSaveLoading(false);
    }
  };

  // Handle password form input
  const handlePwChange = (e) => {
    setPwForm({ ...pwForm, [e.target.name]: e.target.value });
    setPwError('');
  };

  // Toast style options
  const toastOptions = (type) => ({
    position: 'top-right',
    style: {
      background: type === 'success' ? '#d1fae5' : '#fee2e2',
      color: type === 'success' ? '#10B981' : '#B91C1C',
      borderRadius: 8,
      fontWeight: 500,
    },
    progressStyle: { background: type === 'success' ? '#10B981' : '#ef4444' },
    autoClose: 3000,
  });

  // Change password
  const handleChangePassword = async (e) => {
    e.preventDefault();
    // Inline validation
    if (!pwForm.current || !pwForm.new1 || !pwForm.new2) {
      setPwError('All fields are required.');
      return;
    }
    if (pwForm.current === pwForm.new1) {
      setPwError('New password must be different from current password.');
      return;
    }
    if (!validatePassword(pwForm.new1)) {
      setPwError('New password does not meet requirements.');
      return;
    }
    if (pwForm.new1 !== pwForm.new2) {
      setPwError('The passwords do not match.');
      return;
    }
    setPwLoading(true);
    try {
      const resp = await fetch(`${API_BASE}/api/profile/change-password/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          current_password: pwForm.current,
          new_password: pwForm.new1,
        }),
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || 'Failed to change password');
      toast.success('Password changed successfully!', toastOptions('success'));
      setPwForm({ current: '', new1: '', new2: '' });
    } catch (e) {
      toast.error(
        e.message || 'Failed to change password.',
        toastOptions('error'),
      );
    } finally {
      setPwLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[200px]">
        <span className="text-lg text-[#6B7280]">Loading profile...</span>
      </div>
    );
  }
  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[200px]">
        <span className="text-lg text-red-500">{error}</span>
      </div>
    );
  }

  return (
    <div className="space-y-10 max-w-2xl mx-auto px-2 md:px-0">
      <ToastContainer containerId="profile-toast" position="top-center" />
      <div aria-live="polite" className="sr-only">
        {ariaMessage}
      </div>
      {/* Profile Info Card */}
      <div className="profile-card mb-8 p-8 bg-white dark:bg-[#23272F] shadow-xl rounded-2xl flex flex-col gap-2">
        <h2 className="text-4xl font-extrabold mb-2 text-emerald-600 dark:text-emerald-400">
          Profile
        </h2>
        <p className="text-gray-400 mb-6 text-lg">
          View and edit your account settings here
        </p>
        {!editMode ? (
          <div className="space-y-2">
            <div>
              <span
                className="font-semibold dark:text-[#F3F4F6]"
                style={{ color: theme === 'dark' ? '#F3F4F6' : '#000000' }}
              >
                Name:
              </span>{' '}
              <span
                className="dark:text-[#D1D5DB]"
                style={{ color: theme === 'dark' ? '#D1D5DB' : '#1F2937' }}
              >
                {profile.name || (
                  <span
                    className="italic dark:text-[#9CA3AF]"
                    style={{ color: theme === 'dark' ? '#9CA3AF' : '#6B7280' }}
                  >
                    (not set)
                  </span>
                )}
              </span>
            </div>
            <div>
              <span
                className="font-semibold dark:text-[#F3F4F6]"
                style={{ color: theme === 'dark' ? '#F3F4F6' : '#000000' }}
              >
                Email:
              </span>{' '}
              <span
                className="dark:text-[#D1D5DB]"
                style={{ color: theme === 'dark' ? '#D1D5DB' : '#1F2937' }}
              >
                {profile.email}
              </span>
            </div>
            <button
              className="mt-4 px-4 py-2 bg-[#10B981] text-white rounded hover:bg-[#059669] focus:outline-none focus:ring-2 focus:ring-[#10B981]"
              onClick={() => {
                setEditMode(true);
                setEditProfile(profile);
              }}
            >
              Edit Profile
            </button>
          </div>
        ) : (
          <form className="space-y-4" onSubmit={handleSaveProfile}>
            <div>
              <label
                htmlFor="profile-name"
                className="block font-semibold mb-1 text-[#374151] dark:text-[#F3F4F6]"
              >
                Name
              </label>
              <input
                id="profile-name"
                type="text"
                name="name"
                value={editProfile.name}
                onChange={handleEditChange}
                className="profile-input"
                placeholder="Your name"
                autoComplete="name"
              />
            </div>
            <div>
              <label
                htmlFor="profile-email"
                className="block font-semibold mb-1 text-[#374151] dark:text-[#F3F4F6]"
              >
                Email
              </label>
              <input
                id="profile-email"
                type="email"
                name="email"
                value={editProfile.email}
                onChange={handleEditChange}
                className="profile-input"
                placeholder="your@email.com"
                autoComplete="email"
                required
              />
            </div>
            <div className="flex gap-2 mt-2">
              <button
                type="submit"
                className="px-4 py-2 bg-[#10B981] text-white rounded hover:bg-[#059669] focus:outline-none focus:ring-2 focus:ring-[#10B981]"
                disabled={saveLoading}
              >
                {saveLoading ? 'Saving...' : 'Save'}
              </button>
              <button
                type="button"
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-400"
                onClick={() => {
                  setEditMode(false);
                  setEditProfile(profile);
                }}
                disabled={saveLoading}
              >
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>

      {/* Password Change Card */}
      <div className="profile-card p-8 bg-white dark:bg-[#23272F] shadow-xl rounded-2xl flex flex-col gap-2">
        <h3 className="text-2xl font-bold mb-4 text-emerald-600 dark:text-emerald-400">
          Change Password
        </h3>
        <form className="space-y-6" onSubmit={handleChangePassword}>
          {/* Current Password Field with show/hide icon */}
          <div className="relative">
            <label
              htmlFor="pw-current"
              className="block font-semibold mb-1 text-[#374151] dark:text-gray-200"
            >
              Current Password
            </label>
            <input
              id="pw-current"
              type={showPw.current ? 'text' : 'password'}
              name="current"
              value={pwForm.current}
              onChange={handlePwChange}
              className="profile-input pr-10"
              placeholder="Enter your current password"
              autoComplete="current-password"
              required
            />
            <button
              type="button"
              aria-label={showPw.current ? 'Hide password' : 'Show password'}
              className="show-hide-btn"
              onClick={() => setShowPw((s) => ({ ...s, current: !s.current }))}
              tabIndex={0}
            >
              {showPw.current ? <FaEyeSlash /> : <FaEye />}
            </button>
          </div>
          {/* New Password Field with show/hide icon and helper text */}
          <div className="relative">
            <label
              htmlFor="pw-new1"
              className="block font-semibold mb-1 text-[#374151] dark:text-gray-200"
            >
              New Password
            </label>
            <input
              id="pw-new1"
              type={showPw.new1 ? 'text' : 'password'}
              name="new1"
              value={pwForm.new1}
              onChange={handlePwChange}
              onFocus={() => setPwFocused(true)}
              onBlur={() => setPwFocused(false)}
              className="profile-input pr-10"
              placeholder="Enter your new password"
              autoComplete="new-password"
              required
              aria-describedby="pw-reqs"
            />
            <button
              type="button"
              aria-label={showPw.new1 ? 'Hide password' : 'Show password'}
              className="show-hide-btn"
              onClick={() => setShowPw((s) => ({ ...s, new1: !s.new1 }))}
              tabIndex={0}
            >
              {showPw.new1 ? <FaEyeSlash /> : <FaEye />}
            </button>
            {(pwFocused || pwForm.new1) && (
              <ul id="pw-reqs" className="password-requirements-list mt-2">
                {passwordRules.map((rule) => {
                  const passed = rule.test(pwForm.new1);
                  return (
                    <li
                      key={rule.message}
                      className={
                        passed
                          ? 'requirement-met flex items-center'
                          : 'requirement-unmet flex items-center'
                      }
                    >
                      <span className="mr-1">{passed ? '✓' : '✗'}</span>
                      {rule.message}
                    </li>
                  );
                })}
              </ul>
            )}
            {pwForm.current &&
              pwForm.new1 &&
              pwForm.current === pwForm.new1 && (
              <div className="text-red-500 text-sm mt-1">
                  New password must be different from current password.
              </div>
            )}
          </div>
          {/* Confirm New Password Field with show/hide icon */}
          <div className="relative">
            <label
              htmlFor="pw-new2"
              className="block font-semibold mb-1 text-[#374151] dark:text-gray-200"
            >
              Confirm New Password
            </label>
            <input
              id="pw-new2"
              type={showPw.new2 ? 'text' : 'password'}
              name="new2"
              value={pwForm.new2}
              onChange={handlePwChange}
              className="profile-input pr-10"
              placeholder="Confirm your new password"
              autoComplete="new-password"
              required
            />
            <button
              type="button"
              aria-label={showPw.new2 ? 'Hide password' : 'Show password'}
              className="show-hide-btn"
              onClick={() => setShowPw((s) => ({ ...s, new2: !s.new2 }))}
              tabIndex={0}
            >
              {showPw.new2 ? <FaEyeSlash /> : <FaEye />}
            </button>
            {pwForm.new2 && pwForm.new1 !== pwForm.new2 && (
              <div className="text-red-500 text-sm mt-1">
                The passwords do not match.
              </div>
            )}
          </div>
          {pwError && (
            <div className="text-red-500 text-sm mt-1">{pwError}</div>
          )}
          <div className="flex flex-col md:flex-row gap-2 mt-2">
            <button
              type="submit"
              className="w-full md:w-auto px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-bold flex items-center justify-center gap-2 transition"
              disabled={pwLoading}
            >
              {pwLoading ? <span className="loader"></span> : 'Change Password'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

Profile.propTypes = {
  accessToken: PropTypes.string.isRequired,
  theme: PropTypes.string.isRequired,
};

export default Profile;
