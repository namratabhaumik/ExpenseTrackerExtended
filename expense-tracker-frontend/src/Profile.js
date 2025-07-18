import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

function Profile({ accessToken }) {
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
    <div className="space-y-8 max-w-2xl mx-auto">
      <ToastContainer />
      {/* Profile Info Card */}
      <div className="card mb-6 p-6 bg-white dark:bg-[#23272F] shadow rounded-lg">
        <h2 className="text-3xl font-bold mb-2 text-[#4B5563]">Profile</h2>
        <p className="text-[#9CA3AF] mb-4">
          View and edit your account settings here
        </p>
        {!editMode ? (
          <div className="space-y-2">
            <div>
              <span className="font-semibold text-[#374151] dark:text-[#F3F4F6]">
                Name:
              </span>{' '}
              <span className="text-[#4B5563] dark:text-[#D1D5DB]">
                {profile.name || (
                  <span className="italic text-[#9CA3AF]">(not set)</span>
                )}
              </span>
            </div>
            <div>
              <span className="font-semibold text-[#374151] dark:text-[#F3F4F6]">
                Email:
              </span>{' '}
              <span className="text-[#4B5563] dark:text-[#D1D5DB]">
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
                className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-[#10B981] dark:bg-[#23272F] dark:text-[#F3F4F6]"
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
                className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-[#10B981] dark:bg-[#23272F] dark:text-[#F3F4F6]"
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
      <div className="card p-6 bg-white dark:bg-[#23272F] shadow rounded-lg">
        <h3 className="text-xl font-semibold mb-2 text-[#4B5563]">
          Change Password
        </h3>
        <form className="space-y-4" onSubmit={handleChangePassword}>
          <div>
            <label
              htmlFor="pw-current"
              className="block font-semibold mb-1 text-[#374151] dark:text-[#F3F4F6]"
            >
              Current Password
            </label>
            <input
              id="pw-current"
              type="password"
              name="current"
              value={pwForm.current}
              onChange={handlePwChange}
              className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-[#10B981] dark:bg-[#23272F] dark:text-[#F3F4F6]"
              autoComplete="current-password"
              required
            />
          </div>
          <div>
            <label
              htmlFor="pw-new1"
              className="block font-semibold mb-1 text-[#374151] dark:text-[#F3F4F6]"
            >
              New Password
            </label>
            <input
              id="pw-new1"
              type="password"
              name="new1"
              value={pwForm.new1}
              onChange={handlePwChange}
              onFocus={() => setPwFocused(true)}
              onBlur={() => setPwFocused(false)}
              className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-[#10B981] dark:bg-[#23272F] dark:text-[#F3F4F6]"
              autoComplete="new-password"
              required
            />
            {/* Inline password requirements */}
            {(pwFocused || pwForm.new1) && (
              <ul className="password-requirements-list mt-2">
                {passwordRules.map((rule) => {
                  const passed = rule.test(pwForm.new1);
                  return (
                    <li
                      key={rule.message}
                      className={
                        passed
                          ? 'requirement-met text-green-600 flex items-center'
                          : 'requirement-unmet text-red-500 flex items-center'
                      }
                    >
                      <span className="mr-1">{passed ? '✓' : '✗'}</span>
                      {rule.message}
                    </li>
                  );
                })}
              </ul>
            )}
            {/* Inline error if new password matches current password */}
            {pwForm.current &&
              pwForm.new1 &&
              pwForm.current === pwForm.new1 && (
              <div className="text-red-500 text-sm mt-1">
                  New password must be different from current password.
              </div>
            )}
          </div>
          <div>
            <label
              htmlFor="pw-new2"
              className="block font-semibold mb-1 text-[#374151] dark:text-[#F3F4F6]"
            >
              Confirm New Password
            </label>
            <input
              id="pw-new2"
              type="password"
              name="new2"
              value={pwForm.new2}
              onChange={handlePwChange}
              className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-[#10B981] dark:bg-[#23272F] dark:text-[#F3F4F6]"
              autoComplete="new-password"
              required
            />
            {/* Inline match error */}
            {pwForm.new2 && pwForm.new1 !== pwForm.new2 && (
              <div className="text-red-500 text-sm mt-1">
                The passwords do not match.
              </div>
            )}
          </div>
          {pwError && (
            <div className="text-red-500 text-sm mt-1">{pwError}</div>
          )}
          <div className="flex gap-2 mt-2">
            <button
              type="submit"
              className="px-4 py-2 bg-[#10B981] text-white rounded hover:bg-[#059669] focus:outline-none focus:ring-2 focus:ring-[#10B981]"
              disabled={pwLoading}
            >
              {pwLoading ? 'Changing...' : 'Change Password'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

Profile.propTypes = {
  accessToken: PropTypes.string.isRequired,
};

export default Profile;
