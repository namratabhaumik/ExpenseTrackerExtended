import React from 'react';

function Profile() {
  return (
    <div className="space-y-6">
      {/* Main Profile Card */}
      <div className="card mb-6">
        <h2 className="text-3xl font-bold mb-4" style={{ color: '#4B5563' }}>
          Profile
        </h2>
        <p className="text-[#9CA3AF] mb-6">
          View and edit your account settings here
        </p>

        {/* Static Placeholder Content */}
        <div className="text-center py-8">
          <p className="text-[#9CA3AF] text-lg">
            Profile management coming soon...
          </p>
        </div>
      </div>

      {/* Additional Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="stat-card">
          <h3
            className="text-xl font-semibold mb-2"
            style={{ color: '#4B5563' }}
          >
            Account Settings
          </h3>
          <p className="text-[#9CA3AF] text-sm">
            Update your email, password, and preferences
          </p>
        </div>

        <div className="stat-card">
          <h3
            className="text-xl font-semibold mb-2"
            style={{ color: '#4B5563' }}
          >
            Security
          </h3>
          <p className="text-[#9CA3AF] text-sm">
            Manage your account security and privacy settings
          </p>
        </div>
      </div>
    </div>
  );
}

export default Profile;
