import React from 'react';

function Categories() {
  return (
    <div className="space-y-6">
      {/* Main Categories Card */}
      <div className="card mb-6">
        <h2 className="text-3xl font-bold mb-4" style={{ color: '#4B5563' }}>
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
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="stat-card">
          <h3
            className="text-xl font-semibold mb-2"
            style={{ color: '#4B5563' }}
          >
            Category Overview
          </h3>
          <p className="text-[#9CA3AF] text-sm">
            View spending patterns and category breakdowns
          </p>
        </div>

        <div className="stat-card">
          <h3
            className="text-xl font-semibold mb-2"
            style={{ color: '#4B5563' }}
          >
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
