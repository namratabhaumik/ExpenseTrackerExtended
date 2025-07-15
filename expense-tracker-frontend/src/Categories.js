import React from 'react';

function Categories() {
  return (
    <div className="space-y-6">
      {/* Main Categories Card */}
      <div className="bg-white dark:bg-[#23272F] rounded-xl shadow-md p-6 border border-[#E5E7EB] dark:border-[#4B5563]">
        <h2 className="text-2xl font-bold text-[#4B5563] dark:text-[#F3F4F6] mb-4">
          Categories
        </h2>
        <p className="text-[#9CA3AF] mb-6">
          Track and manage your spending categories here
        </p>

        {/* Static Placeholder Content */}
        <div className="text-center py-8">
          <p className="text-[#9CA3AF] text-lg">
            Categories management coming soon...
          </p>
        </div>
      </div>

      {/* Additional Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white dark:bg-[#23272F] rounded-xl shadow-md p-6 border border-[#E5E7EB] dark:border-[#4B5563]">
          <h3 className="text-lg font-semibold text-[#4B5563] dark:text-[#F3F4F6] mb-2">
            Category Overview
          </h3>
          <p className="text-[#9CA3AF] text-sm">
            View spending patterns and category breakdowns
          </p>
        </div>

        <div className="bg-white dark:bg-[#23272F] rounded-xl shadow-md p-6 border border-[#E5E7EB] dark:border-[#4B5563]">
          <h3 className="text-lg font-semibold text-[#4B5563] dark:text-[#F3F4F6] mb-2">
            Custom Categories
          </h3>
          <p className="text-[#9CA3AF] text-sm">
            Create and manage your own spending categories
          </p>
        </div>
      </div>
    </div>
  );
}

export default Categories;
