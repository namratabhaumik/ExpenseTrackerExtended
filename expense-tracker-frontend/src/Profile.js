import React from 'react';

function Profile() {
  return (
    <div className="space-y-6">
      {/* Main Profile Card */}
      <div className="bg-white dark:bg-[#23272F] rounded-xl shadow-md p-6 border border-[#E5E7EB] dark:border-[#4B5563]">
        <h2 className="text-2xl font-bold text-[#4B5563] dark:text-[#F3F4F6] mb-4">
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
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white dark:bg-[#23272F] rounded-xl shadow-md p-6 border border-[#E5E7EB] dark:border-[#4B5563]">
          <h3 className="text-lg font-semibold text-[#4B5563] dark:text-[#F3F4F6] mb-2">
            Account Settings
          </h3>
          <p className="text-[#9CA3AF] text-sm">
            Update your email, password, and preferences
          </p>
        </div>

        <div className="bg-white dark:bg-[#23272F] rounded-xl shadow-md p-6 border border-[#E5E7EB] dark:border-[#4B5563]">
          <h3 className="text-lg font-semibold text-[#4B5563] dark:text-[#F3F4F6] mb-2">
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
