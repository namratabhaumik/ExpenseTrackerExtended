import React, { useEffect, useState, useRef } from 'react';
import PropTypes from 'prop-types';
import { apiGet } from '../../services/api';
import { API_ENDPOINTS } from '../../utils/constants';
import './Dashboard.css';

// Dummy data for fallback - moved outside component to prevent recreation
const DUMMY_EXPENSES = [
  {
    id: 1,
    amount: 50.0,
    category: 'Food',
    description: 'Lunch',
    timestamp: '2025-01-12T10:30:00Z',
  },
  {
    id: 2,
    amount: 25.0,
    category: 'Transport',
    description: 'Bus fare',
    timestamp: '2025-01-11T08:15:00Z',
  },
  {
    id: 3,
    amount: 120.0,
    category: 'Shopping',
    description: 'Groceries',
    timestamp: '2025-01-10T16:45:00Z',
  },
  {
    id: 4,
    amount: 35.0,
    category: 'Entertainment',
    description: 'Movie ticket',
    timestamp: '2025-01-09T19:20:00Z',
  },
  {
    id: 5,
    amount: 80.0,
    category: 'Food',
    description: 'Dinner',
    timestamp: '2025-01-08T20:00:00Z',
  },
];

function Dashboard({ refreshFlag }) {
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const isMountedRef = useRef(true);
  const abortControllerRef = useRef(null);

  // Fetch expenses on mount
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
    };
  }, []);

  // Calculate total expenses
  const totalExpenses = expenses.reduce(
    (sum, exp) => sum + Number(exp.amount),
    0,
  );

  // Get 5 most recent expenses
  const recentExpenses = expenses
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    .slice(0, 5);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-8">
      {/* Summary Card */}
      <div className="dashboard-card bg-[#f3f4f6] dark:bg-[#23272F] rounded-xl shadow-md p-8 border border-[#E5E7EB] dark:border-[#4B5563]">
        <h2 className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">
          Dashboard Summary
        </h2>
        <div className="dashboard-grid grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="stat-card bg-[#fdfdfd] dark:bg-[#181A20] rounded-lg p-6 border border-[#E5E7EB] dark:border-[#4B5563] hover:shadow-md transition-shadow duration-200">
            <div className="text-[#9CA3AF] text-sm font-medium mb-2">
              Total Expenses
            </div>
            <div className="text-3xl font-bold text-[#10B981]">
              ${totalExpenses.toFixed(2)}
            </div>
          </div>
          <div className="stat-card bg-[#fdfdfd] dark:bg-[#181A20] rounded-lg p-6 border border-[#E5E7EB] dark:border-[#4B5563] hover:shadow-md transition-shadow duration-200">
            <div className="text-[#9CA3AF] text-sm font-medium mb-2">
              Total Transactions
            </div>
            <div className="text-3xl font-bold" style={{ color: '#4B5563' }}>
              {expenses.length}
            </div>
          </div>
          <div className="stat-card bg-[#fdfdfd] dark:bg-[#181A20] rounded-lg p-6 border border-[#E5E7EB] dark:border-[#4B5563] hover:shadow-md transition-shadow duration-200">
            <div className="text-[#9CA3AF] text-sm font-medium mb-2">
              Average per Transaction
            </div>
            <div className="text-3xl font-bold" style={{ color: '#4B5563' }}>
              $
              {expenses.length > 0
                ? (totalExpenses / expenses.length).toFixed(2)
                : '0.00'}
            </div>
          </div>
        </div>
      </div>

      {/* Recent Expenses Table */}
      <div className="mt-8">
        <h3 className="text-xl font-semibold text-emerald-600 dark:text-emerald-400 mb-4">
          Recent Expenses
        </h3>
        {loading ? (
          <div className="text-center py-12">
            <div className="text-[#9CA3AF] text-lg">
              Loading recent expenses...
            </div>
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <div className="text-red-500 mb-3 text-lg">{error}</div>
            <div className="text-[#9CA3AF] text-sm">Showing sample data</div>
          </div>
        ) : recentExpenses.length === 0 ? (
          <div className="text-center py-12 flex flex-col items-center justify-center gap-4">
            {/* Spinner */}
            <div
              className="dashboard-spinner"
              aria-label="No expenses illustration"
              role="img"
            >
              <svg
                width="80"
                height="80"
                viewBox="0 0 80 80"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <circle
                  cx="40"
                  cy="40"
                  r="36"
                  stroke="#5eead4"
                  strokeWidth="6"
                  fill="#f9fafb"
                />
                <path
                  d="M24 48c4-8 28-8 32 0"
                  stroke="#10b981"
                  strokeWidth="3"
                  strokeLinecap="round"
                  fill="none"
                />
                <circle cx="32" cy="34" r="3" fill="#10b981" />
                <circle cx="48" cy="34" r="3" fill="#10b981" />
              </svg>
            </div>
            <div className="dashboard-empty text-[#9CA3AF] text-lg dark:text-[#6EE7B7]">
              No expenses found.
              <br />
              Start tracking your spending!
            </div>
          </div>
        ) : (
          <div className="overflow-x-auto">
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
                {recentExpenses.map((expense, idx) => (
                  <tr
                    key={expense.id}
                    className={
                      'border-b border-[#E5E7EB] hover:bg-[#E0F7F4] transition-colors duration-150'
                    }
                  >
                    <td className="py-3 px-4 text-[#10B981] font-semibold">
                      ${Number(expense.amount).toFixed(2)}
                    </td>
                    <td className="py-3 px-4 text-[#9CA3AF]">
                      {expense.category}
                    </td>
                    <td className="py-3 px-4 text-[#9CA3AF]">
                      {expense.description}
                    </td>
                    <td className="py-3 px-4 text-[#9CA3AF] text-sm">
                      {new Date(expense.timestamp).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

Dashboard.propTypes = {};

export default Dashboard;
