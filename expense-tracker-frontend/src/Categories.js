import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

const Categories = ({ accessToken, onNavigate }) => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchCategories = async () => {
    try {
      setLoading(true);
      setError('');

      // Fetch all expenses using the same pattern as Expenses component
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/expenses/list/`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
          credentials: 'include',
        },
      );

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || 'Failed to fetch expenses');
      }

      const data = await response.json();
      const expenses = data.expenses || [];

      // Group expenses by category
      const categoryMap = {};
      expenses.forEach((expense) => {
        const category = expense.category || 'Uncategorized';
        if (!categoryMap[category]) {
          categoryMap[category] = {
            name: category,
            totalSpent: 0,
            expenseCount: 0,
            expenses: [],
          };
        }
        categoryMap[category].totalSpent += parseFloat(expense.amount);
        categoryMap[category].expenseCount += 1;
        categoryMap[category].expenses.push(expense);
      });

      // Convert to array and sort by total spent
      const categoryList = Object.values(categoryMap).sort(
        (a, b) => b.totalSpent - a.totalSpent,
      );

      setCategories(categoryList);
    } catch (error) {
      setError(error.message || 'An error occurred while fetching categories.');
      setCategories([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!accessToken) return;
    fetchCategories();
  }, [accessToken]);

  const handleViewExpenses = (categoryName) => {
    // Navigate to Expenses tab with category filter
    if (onNavigate) {
      // Set URL parameters for category filtering
      const url = new URL(window.location);
      url.searchParams.set('category', categoryName);
      window.history.pushState({}, '', url);

      // Navigate to expenses page
      onNavigate('expenses');

      // Clear the URL parameter after a short delay to ensure navigation completes
      // This ensures that when users navigate away and come back, they see all expenses
      setTimeout(() => {
        const cleanUrl = new URL(window.location);
        cleanUrl.searchParams.delete('category');
        window.history.replaceState({}, '', cleanUrl);
      }, 500);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="card mb-6">
          <h2 className="text-3xl font-bold mb-4" style={{ color: '#4B5563' }}>
            Categories
          </h2>
          <p className="text-[#9CA3AF] mb-6">
            Track and manage your spending categories here
          </p>
          <div className="text-center py-8">
            <p className="text-[#9CA3AF] text-lg">Loading categories...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="card mb-6">
          <h2 className="text-3xl font-bold mb-4" style={{ color: '#4B5563' }}>
            Categories
          </h2>
          <p className="text-[#9CA3AF] mb-6">
            Track and manage your spending categories here
          </p>
          <div className="text-center py-8">
            <p className="text-red-500 text-lg">Error: {error}</p>
          </div>
        </div>
      </div>
    );
  }

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

        {categories.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-[#9CA3AF] text-lg">
              No categories found. Add some expenses to see categories here.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {categories.map((category, index) => (
              <div
                key={index}
                className="stat-card cursor-pointer"
                onClick={() => handleViewExpenses(category.name)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    handleViewExpenses(category.name);
                  }
                }}
              >
                <h3
                  className="text-xl font-semibold mb-2"
                  style={{ color: '#4B5563' }}
                >
                  {category.name}
                </h3>
                <div
                  className="text-2xl font-bold mb-1"
                  style={{ color: '#10B981' }}
                >
                  ${category.totalSpent.toFixed(2)}
                </div>
                <div className="text-[#9CA3AF] mb-4">
                  {category.expenseCount} expense
                  {category.expenseCount !== 1 ? 's' : ''}
                </div>
                <button
                  className="w-full text-white font-medium py-2 px-4 rounded transition-colors"
                  style={{ backgroundColor: '#10B981' }}
                  onMouseEnter={(e) => {
                    e.target.style.backgroundColor = '#14B8A6';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.backgroundColor = '#10B981';
                  }}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleViewExpenses(category.name);
                  }}
                >
                  View Expenses
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

Categories.propTypes = {
  accessToken: PropTypes.string,
  onNavigate: PropTypes.func,
};

export default Categories;
