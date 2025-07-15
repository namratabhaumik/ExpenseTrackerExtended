import React, { useEffect, useState, useRef } from 'react';
import PropTypes from 'prop-types';
import './styles/Expenses.css';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { ClipLoader } from 'react-spinners';

function Expenses({ onLogout, accessToken, setDashboardRefreshFlag }) {
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [form, setForm] = useState({
    amount: '',
    category: '',
    description: '',
  });
  const [addError, setAddError] = useState('');
  const [addSuccess, setAddSuccess] = useState('');
  // Receipt upload state
  const [receiptFile, setReceiptFile] = useState(null);
  const [receiptFilename, setReceiptFilename] = useState('');
  const [receiptExpenseId, setReceiptExpenseId] = useState('');
  const [receiptStatus, setReceiptStatus] = useState('');
  // New: Sorting and filtering state
  const [sortBy, setSortBy] = useState('date_desc');
  const [categoryFilter, setCategoryFilter] = useState('');
  // Loading states for forms
  const [loginLoading, setLoginLoading] = useState(false);
  const [receiptLoading, setReceiptLoading] = useState(false);
  const [refreshFlag, setRefreshFlag] = useState(0);

  // Refs to prevent infinite loops
  const isMountedRef = useRef(true);
  const abortControllerRef = useRef(null);

  // Helper: fetch expenses from backend
  const fetchExpenses = async () => {
    if (!isMountedRef.current) return;
    setLoading(true);
    setError('');
    try {
      const resp = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/expenses/list/`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
          credentials: 'include',
        },
      );
      if (!isMountedRef.current) return;
      if (!resp.ok) {
        const err = await resp.json();
        setError(err.error || 'Failed to fetch expenses');
        setExpenses([]);
      } else {
        const data = await resp.json();
        // Normalize: always use 'id'
        const normalized = (data.expenses || []).map((exp) => ({
          id: exp.id || exp.expense_id,
          amount: exp.amount,
          category: exp.category,
          description: exp.description,
          timestamp: exp.timestamp,
        }));
        setExpenses(normalized);
      }
    } catch (e) {
      if (e.name === 'AbortError') return;
      if (isMountedRef.current) {
        setError('An error occurred while fetching expenses.');
        setExpenses([]);
      }
    } finally {
      if (isMountedRef.current) setLoading(false);
    }
  };

  // Fetch expenses on mount and when accessToken changes
  useEffect(() => {
    if (!accessToken) return;

    setLoading(true);
    setError('');
    fetch(`${process.env.REACT_APP_BACKEND_URL}/api/expenses/list/`, {
      headers: { Authorization: `Bearer ${accessToken}` },
      credentials: 'include',
    })
      .then((resp) => {
        if (!resp.ok)
          return resp.json().then((err) => {
            throw new Error(err.error || 'Failed to fetch expenses');
          });
        return resp.json();
      })
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
  }, [accessToken, refreshFlag]);

  // Add this effect ONCE to handle unmount:
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  // Handle form input
  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // Handle add expense
  const handleAddExpense = async (e) => {
    e.preventDefault();
    setAddError('');
    setAddSuccess('');
    setLoginLoading(true);
    toast.dismiss(); // Clear previous toasts
    try {
      const resp = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/expenses/`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${accessToken}`,
          },
          credentials: 'include',
          body: JSON.stringify(form),
        },
      );
      if (!resp.ok) {
        const err = await resp.json();
        setAddError(err.error || 'Failed to add expense');
        toast.error(err.error || 'Failed to add expense', {
          position: 'top-right',
          style: {
            background: '#fee2e2',
            color: '#4B5563',
            borderRadius: 8,
            fontWeight: 500,
          },
          progressStyle: { background: '#ef4444' },
        });
      } else {
        setAddSuccess('Expense added successfully!');
        setForm({ amount: '', category: '', description: '' });
        setRefreshFlag((f) => f + 1); // <-- trigger refetch for Expenses
        if (setDashboardRefreshFlag) setDashboardRefreshFlag((f) => f + 1); // <-- trigger refetch for Dashboard
        toast.success('Expense added successfully!', {
          position: 'top-right',
          style: {
            background: '#d1fae5',
            color: '#10B981', // emerald
            borderRadius: 8,
            fontWeight: 500,
          },
          progressStyle: { background: '#14B8A6' }, // teal
        });
      }
    } catch (e) {
      setAddError('An error occurred while adding expense.');
      toast.error('An error occurred while adding expense.', {
        position: 'top-right',
        style: {
          background: '#fee2e2',
          color: '#4B5563',
          borderRadius: 8,
          fontWeight: 500,
        },
        progressStyle: { background: '#ef4444' },
      });
    } finally {
      setLoginLoading(false);
    }
  };

  // Handle receipt file change
  const handleReceiptFileChange = (e) => {
    setReceiptFile(e.target.files[0]);
    setReceiptFilename(e.target.files[0]?.name || '');
  };

  // Handle receipt upload
  const handleReceiptUpload = async (e) => {
    e.preventDefault();
    setReceiptStatus('');
    if (!receiptFile) {
      setReceiptStatus('Please select a file.');
      toast.dismiss(); // Clear previous toasts
      toast.error('Please select a file.', {
        position: 'top-right',
        style: {
          background: '#fee2e2',
          color: '#4B5563',
          borderRadius: 8,
          fontWeight: 500,
        },
        progressStyle: { background: '#ef4444' },
      });
      return;
    }
    setReceiptLoading(true);
    toast.dismiss(); // Clear previous toasts
    // Read file as base64
    const reader = new window.FileReader();
    reader.onload = async () => {
      const base64Data = reader.result.split(',')[1];
      const payload = {
        file: base64Data,
        filename: receiptFilename,
      };
      if (receiptExpenseId) payload.expense_id = receiptExpenseId;
      try {
        const resp = await fetch(
          `${process.env.REACT_APP_BACKEND_URL}/api/receipts/upload/`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${accessToken}`,
            },
            credentials: 'include',
            body: JSON.stringify(payload),
          },
        );
        const data = await resp.json();
        if (!resp.ok) {
          setReceiptStatus(data.error || 'Failed to upload receipt');
          toast.error(data.error || 'Failed to upload receipt', {
            position: 'top-right',
            style: {
              background: '#fee2e2',
              color: '#4B5563',
              borderRadius: 8,
              fontWeight: 500,
            },
            progressStyle: { background: '#ef4444' },
          });
        } else {
          setReceiptStatus('Receipt uploaded successfully!');
          setReceiptFile(null);
          setReceiptFilename('');
          setReceiptExpenseId('');
          toast.success('Receipt uploaded successfully!', {
            position: 'top-right',
            style: {
              background: '#d1fae5',
              color: '#2563EB',
              borderRadius: 8,
              fontWeight: 500,
            },
            progressStyle: { background: '#10b981' },
          });
        }
      } catch (e) {
        setReceiptStatus('An error occurred while uploading receipt.');
        toast.error('An error occurred while uploading receipt.', {
          position: 'top-right',
          style: {
            background: '#fee2e2',
            color: '#4B5563',
            borderRadius: 8,
            fontWeight: 500,
          },
          progressStyle: { background: '#ef4444' },
        });
      } finally {
        setReceiptLoading(false);
      }
    };
    reader.readAsDataURL(receiptFile);
  };

  // --- Derived: filtered and sorted expenses ---
  const filteredExpenses = expenses.filter((exp) =>
    categoryFilter.trim() === ''
      ? true
      : exp.category.toLowerCase().includes(categoryFilter.trim().toLowerCase()),
  );
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

  console.log(
    'Expenses to render:',
    sortedExpenses,
    'Loading:',
    loading,
    'Error:',
    error,
  );

  return (
    <div className="expenses-container">
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
      <h2>Expenses</h2>
      {/* Summary Card and Controls */}
      <div className="w-full flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4 flex-1 min-w-[220px] border border-[#E5E7EB] flex flex-col items-center md:items-start">
          <span className="text-[#9CA3AF] text-sm font-medium mb-1">
            Total Expenses
          </span>
          <span className="text-2xl font-bold text-[#10B981]">
            ${totalExpenses.toFixed(2)}
          </span>
        </div>
        <div className="flex flex-col md:flex-row gap-2 md:gap-4 items-center">
          <label
            className="text-[#4B5563] font-medium text-sm"
            htmlFor="sort-by"
          >
            Sort by:
          </label>
          <select
            id="sort-by"
            className="border border-[#9CA3AF] rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#2563EB] text-[#4B5563] bg-white"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="date_desc">Date (Newest)</option>
            <option value="date_asc">Date (Oldest)</option>
            <option value="amount_desc">Amount (High-Low)</option>
            <option value="amount_asc">Amount (Low-High)</option>
          </select>
          <input
            type="text"
            placeholder="Filter by category"
            className="border border-[#9CA3AF] rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#2563EB] text-[#4B5563] bg-white"
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            aria-label="Filter by category"
          />
        </div>
      </div>
      <button className="expenses-logout-btn" onClick={onLogout}>
        Logout
      </button>
      <h3>Add Expense</h3>
      <form
        className="expenses-form"
        onSubmit={handleAddExpense}
        autoComplete="on"
      >
        <input
          type="number"
          name="amount"
          placeholder="Amount"
          value={form.amount}
          onChange={handleChange}
          required
          disabled={loginLoading}
        />
        <input
          type="text"
          name="category"
          placeholder="Category"
          value={form.category}
          onChange={handleChange}
          required
          disabled={loginLoading}
        />
        <input
          type="text"
          name="description"
          placeholder="Description"
          value={form.description}
          onChange={handleChange}
          disabled={loginLoading}
        />
        <button
          type="submit"
          disabled={loginLoading}
          className="flex items-center justify-center gap-2"
        >
          {loginLoading ? <ClipLoader size={20} color="#fff" /> : 'Add'}
        </button>
      </form>
      {addError && <p className="expenses-error">{addError}</p>}
      <h3>Upload Receipt</h3>
      <form className="expenses-receipt-form" onSubmit={handleReceiptUpload}>
        <input
          type="file"
          accept="image/*,.pdf"
          onChange={handleReceiptFileChange}
          disabled={receiptLoading}
        />
        <input
          type="text"
          placeholder="Filename (optional)"
          value={receiptFilename}
          onChange={(e) => setReceiptFilename(e.target.value)}
          disabled={receiptLoading}
        />
        <input
          type="text"
          placeholder="Expense ID (optional)"
          value={receiptExpenseId}
          onChange={(e) => setReceiptExpenseId(e.target.value)}
          disabled={receiptLoading}
        />
        <button
          type="submit"
          disabled={receiptLoading}
          className="flex items-center justify-center gap-2"
        >
          {receiptLoading ? <ClipLoader size={20} color="#fff" /> : 'Upload'}
        </button>
      </form>
      {receiptStatus && (
        <p
          className={
            receiptStatus.includes('success')
              ? 'expenses-success'
              : 'expenses-error'
          }
        >
          {receiptStatus}
        </p>
      )}
      {error && (
        <div className="expenses-error" style={{ marginBottom: 16 }}>
          {error}
        </div>
      )}
      <h3>Your Expenses</h3>
      {error && (
        <div className="expenses-error" style={{ marginBottom: 16 }}>
          {error}
        </div>
      )}
      {/* Render the expenses as a modern table */}
      {!loading && expenses.length > 0 ? (
        <div className="overflow-x-auto mt-4">
          <table className="w-full border border-[#E5E7EB] rounded-lg overflow-hidden">
            <thead className="bg-[#F9FAFB]">
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
                  className={`border-b border-[#E5E7EB] hover:bg-[#E0F7F4] transition-colors duration-150 ${
                    idx % 2 === 0 ? 'bg-white' : 'bg-[#F9FAFB]'
                  }`}
                >
                  <td className="py-3 px-4 text-[#10B981] font-semibold">
                    ${Number(exp.amount).toFixed(2)}
                  </td>
                  <td className="py-3 px-4 text-[#4B5563]">{exp.category}</td>
                  <td className="py-3 px-4 text-[#4B5563]">
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
  onLogout: PropTypes.func.isRequired,
  accessToken: PropTypes.string.isRequired,
  setDashboardRefreshFlag: PropTypes.func,
};

export default Expenses;
