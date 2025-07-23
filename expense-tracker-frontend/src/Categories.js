import React, { useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import { ClipLoader } from 'react-spinners';

const Categories = ({ accessToken, onNavigate }) => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isMounted, setIsMounted] = useState(true);

  const fetchCategories = useCallback(async () => {
    try {
      setLoading(true);
      setError('');

      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/expenses/list/`,
        {
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${accessToken}`,
          },
          credentials: 'include',
        },
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch expenses');
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

      if (isMounted) {
        setCategories(categoryList);
      }
    } catch (err) {
      console.error('Error fetching categories:', err);
      if (isMounted) {
        setError(err.message || 'An error occurred while fetching categories.');
        setCategories([]);
      }
    } finally {
      if (isMounted) {
        setLoading(false);
      }
    }
  }, [isMounted]);

  useEffect(() => {
    fetchCategories();

    return () => {
      setIsMounted(false);
    };
  }, [fetchCategories]);

  const handleViewExpenses = (categoryName) => {
    if (!onNavigate) return;

    // Set URL parameters for category filtering
    const url = new URL(window.location);
    url.searchParams.set('category', categoryName);
    window.history.pushState({}, '', url);

    // Navigate to expenses page
    onNavigate('expenses');

    // Clear the URL parameter after a short delay
    const clearUrlParam = () => {
      const cleanUrl = new URL(window.location);
      cleanUrl.searchParams.delete('category');
      window.history.replaceState({}, '', cleanUrl);
    };

    const timer = setTimeout(clearUrlParam, 500);

    // Cleanup the timer if the component unmounts
    return () => clearTimeout(timer);
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="card mb-6">
          <h2 className="text-3xl font-bold mb-4 text-emerald-600 dark:text-emerald-400">
            Categories
          </h2>
          <p className="text-[#9CA3AF] mb-6">
            Track and manage your spending categories here
          </p>
          <div className="text-center py-8">
            <ClipLoader size={40} color="#10B981" />
            <p className="mt-4 text-gray-500">Loading categories...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="card mb-6">
          <h2 className="text-3xl font-bold mb-4 text-emerald-600 dark:text-emerald-400">
            Categories
          </h2>
          <p className="text-[#9CA3AF] mb-6">
            Track and manage your spending categories here
          </p>
          <div className="bg-red-50 border-l-4 border-red-400 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-red-400"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="card mb-6">
        <h2 className="text-3xl font-bold mb-4 text-emerald-600 dark:text-emerald-400">
          Categories
        </h2>
        <p className="text-[#9CA3AF] mb-6">
          Track and manage your spending categories here
        </p>

        {categories.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500">
              No categories found. Add some expenses to see them categorized
              here.
            </p>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {categories.map((category) => (
              <div
                key={category.name}
                className="p-4 border rounded-lg hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => handleViewExpenses(category.name)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    handleViewExpenses(category.name);
                  }
                }}
              >
                <div className="flex justify-between items-start">
                  <h3 className="font-medium text-lg">{category.name}</h3>
                  <span className="px-2 py-1 bg-emerald-100 text-emerald-800 text-xs font-medium rounded-full">
                    {category.expenseCount}{' '}
                    {category.expenseCount === 1 ? 'expense' : 'expenses'}
                  </span>
                </div>
                <p className="mt-2 text-2xl font-bold">
                  ${category.totalSpent.toFixed(2)}
                </p>
                <div className="mt-2 text-sm text-gray-500">
                  Click to view all {category.name.toLowerCase()} expenses
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

Categories.propTypes = {
  accessToken: PropTypes.string.isRequired,
  onNavigate: PropTypes.func,
};

export default Categories;
