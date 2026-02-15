import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { ClipLoader } from 'react-spinners';
import { showSuccessToast, showErrorToast } from '../../../utils/toast';

function AddExpenseForm({ onSuccess, setDashboardRefreshFlag }) {
  const [form, setForm] = useState({
    amount: '',
    category: '',
    description: '',
  });
  const [addError, setAddError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleAddExpense = async (e) => {
    e.preventDefault();
    setAddError('');
    setLoading(true);
    try {
      const resp = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/expenses/`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify(form),
        },
      );
      if (!resp.ok) {
        const err = await resp.json();
        setAddError(err.error || 'Failed to add expense');
        showErrorToast(err.error || 'Failed to add expense', {
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
        setForm({ amount: '', category: '', description: '' });
        if (onSuccess) onSuccess();
        if (setDashboardRefreshFlag) setDashboardRefreshFlag((f) => f + 1);
        showSuccessToast('Expense added successfully!', {
          position: 'top-right',
          style: {
            background: '#d1fae5',
            color: '#10B981',
            borderRadius: 8,
            fontWeight: 500,
          },
          progressStyle: { background: '#14B8A6' },
        });
      }
    } catch (e) {
      setAddError('An error occurred while adding expense.');
      showErrorToast('An error occurred while adding expense.', {
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
      setLoading(false);
    }
  };

  return (
    <>
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
          disabled={loading}
        />
        <input
          type="text"
          name="category"
          placeholder="Category"
          value={form.category}
          onChange={handleChange}
          required
          disabled={loading}
        />
        <input
          type="text"
          name="description"
          placeholder="Description"
          value={form.description}
          onChange={handleChange}
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading}
          className="flex items-center justify-center gap-2"
        >
          {loading ? <ClipLoader size={20} color="#fff" /> : 'Add'}
        </button>
      </form>
      {addError && <p className="expenses-error">{addError}</p>}
    </>
  );
}

AddExpenseForm.propTypes = {
  onSuccess: PropTypes.func,
  setDashboardRefreshFlag: PropTypes.func,
};

export default AddExpenseForm;
