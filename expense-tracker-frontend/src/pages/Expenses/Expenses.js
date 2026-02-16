import React, { useEffect, useState, useRef } from 'react';
import PropTypes from 'prop-types';
import './Expenses.css';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { apiGet } from '../../services/api';
import { API_ENDPOINTS } from '../../utils/constants';
import AddExpenseForm from './components/AddExpenseForm';
import ReceiptUploadForm from './components/ReceiptUploadForm';
import ExpenseFilters from './components/ExpenseFilters';

function Expenses({ setDashboardRefreshFlag }) {
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  // Sorting and filtering state
  const [sortBy, setSortBy] = useState('date_desc');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [refreshFlag, setRefreshFlag] = useState(0);
  // Support for category filtering via URL params
  const [selectedCategory, setSelectedCategory] = useState('');

  // Refs to prevent infinite loops
  const isMountedRef = useRef(true);

  // Fetch expenses on mount and when refreshFlag changes
  useEffect(() => {
    setLoading(true);
    setError('');
    apiGet(API_ENDPOINTS.EXPENSES_LIST)
      .then((data) => {
        const normalized = (data.expenses || []).map((exp) => ({
          id: exp.id || exp.expense_id,
          amount: exp.amount,
          category: exp.category,
          description: exp.description,
          timestamp: exp.timestamp,
        }));
        setExpenses(normalized);
      })
      .catch((e) => {
        setError(e.message || 'An error occurred while fetching expenses.');
        setExpenses([]);
      })
      .finally(() => setLoading(false));
  }, [refreshFlag]);

  // Add this effect ONCE to handle unmount:
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
      // Clear category filter when component unmounts (user navigates away)
      setCategoryFilter('');
      setSelectedCategory('');
    };
  }, []);

  // In Expenses.js, add support for category filtering via URL params
  useEffect(() => {
    // Check URL params for category filter
    const urlParams = new URLSearchParams(window.location.search);
    const categoryFilter = urlParams.get('category');

    if (categoryFilter) {
      // Only set filter if coming from Categories navigation (URL has category param)
      setSelectedCategory(categoryFilter);
      setCategoryFilter(categoryFilter); // Also set the manual filter to show the selected category
    } else {
      // Clear any existing filters when no URL parameter is present
      setSelectedCategory('');
      setCategoryFilter('');
    }
  }, [window.location.search]); // Re-run when URL changes

  // Handle category filter change
  const handleCategoryFilterChange = (value) => {
    setCategoryFilter(value);
    setSelectedCategory(value); // Keep them in sync
  };

  // Clear category filter
  const clearCategoryFilter = () => {
    setCategoryFilter('');
    setSelectedCategory('');
    // Clear URL parameter
    const url = new URL(window.location);
    url.searchParams.delete('category');
    window.history.replaceState({}, '', url);
  };

  // --- Derived: filtered and sorted expenses ---
  // Collect unique categories for autocomplete
  const allCategories = Array.from(
    new Set(expenses.map((exp) => exp.category).filter(Boolean)),
  );
  const filteredExpenses = expenses.filter((exp) => {
    // Use either the manual filter or the selected category from URL
    const activeFilter = selectedCategory || categoryFilter;

    if (activeFilter.trim() === '') {
      return true;
    }

    return exp.category
      .toLowerCase()
      .includes(activeFilter.trim().toLowerCase());
  });
  const sortedExpenses = [...filteredExpenses].sort((a, b) => {
    if (sortBy === 'date_desc') {
      return new Date(b.timestamp) - new Date(a.timestamp);
    } else if (sortBy === 'date_asc') {
      return new Date(a.timestamp) - new Date(b.timestamp);
    } else if (sortBy === 'amount_desc') {
      return Number(b.amount) - Number(a.amount);
    } else if (sortBy === 'amount_asc') {
      return Number(a.amount) - Number(b.amount);
    }
    return 0;
  });
  const totalExpenses = filteredExpenses.reduce(
    (sum, exp) => sum + Number(exp.amount),
    0,
  );

  return (
    <div className="card expenses-container">
      <ToastContainer
        position="top-right"
        autoClose={3500}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="light"
        className="z-50"
      />
      {/* Removed the redundant <h2>Expenses</h2> heading for clarity */}
      {/* Filters and Summary */}
      <ExpenseFilters
        sortBy={sortBy}
        onSortChange={setSortBy}
        categoryFilter={categoryFilter}
        onCategoryFilterChange={handleCategoryFilterChange}
        categories={allCategories}
        totalExpenses={totalExpenses}
        onClearFilter={clearCategoryFilter}
      />
      {/* Add Expense Form */}
      <AddExpenseForm
        onSuccess={() => setRefreshFlag((f) => f + 1)}
        setDashboardRefreshFlag={setDashboardRefreshFlag}
      />
      {/* Upload Receipt Form */}
      <ReceiptUploadForm />
      {error && (
        <div className="expenses-error" style={{ marginBottom: 16 }}>
          {error}
        </div>
      )}
      <h3>
        Your Expenses
        {categoryFilter && (
          <span className="text-sm font-normal text-[#9CA3AF] ml-2">
            (Filtered by: {categoryFilter})
          </span>
        )}
      </h3>
      {error && (
        <div className="expenses-error" style={{ marginBottom: 16 }}>
          {error}
        </div>
      )}
      {/* Render the expenses as a modern table */}
      {!loading && expenses.length > 0 ? (
        <div className="overflow-x-auto mt-4">
          <table className="dashboard-table w-full border border-[#E5E7EB] rounded-lg overflow-hidden">
            <thead>
              <tr>
                <th className="text-left py-3 px-4 text-[#4B5563] font-semibold text-base border-b border-[#E5E7EB]">
                  Amount
                </th>
                <th className="text-left py-3 px-4 text-[#4B5563] font-semibold text-base border-b border-[#E5E7EB]">
                  Category
                </th>
                <th className="text-left py-3 px-4 text-[#4B5563] font-semibold text-base border-b border-[#E5E7EB]">
                  Description
                </th>
                <th className="text-left py-3 px-4 text-[#4B5563] font-semibold text-base border-b border-[#E5E7EB]">
                  Date
                </th>
              </tr>
            </thead>
            <tbody>
              {sortedExpenses.map((exp, idx) => (
                <tr
                  key={exp.id}
                  className={
                    'border-b border-[#E5E7EB] hover:bg-[#E0F7F4] transition-colors duration-150'
                  }
                >
                  <td className="py-3 px-4 text-[#10B981] font-semibold">
                    ${Number(exp.amount).toFixed(2)}
                  </td>
                  <td className="py-3 px-4 text-[#9CA3AF]">{exp.category}</td>
                  <td className="py-3 px-4 text-[#9CA3AF]">
                    {exp.description}
                  </td>
                  <td className="py-3 px-4 text-[#9CA3AF] text-sm">
                    {new Date(exp.timestamp).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : loading ? (
        <div>Loading...</div>
      ) : (
        <div>No expenses found.</div>
      )}
    </div>
  );
}

Expenses.propTypes = {

  setDashboardRefreshFlag: PropTypes.func,
};

export default Expenses;
