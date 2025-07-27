import React from 'react';
import PropTypes from 'prop-types';
import { ClipLoader } from 'react-spinners';

function AddExpenseForm({ form, onChange, onSubmit, loading, error }) {
  return (
    <form className="expenses-form" onSubmit={onSubmit}>
      <input
        type="number"
        name="amount"
        placeholder="Amount"
        value={form.amount}
        onChange={onChange}
        min="0"
        step="0.01"
        required
        disabled={loading}
      />
      <input
        type="text"
        name="category"
        placeholder="Category"
        value={form.category}
        onChange={onChange}
        required
        disabled={loading}
      />
      <input
        type="text"
        name="description"
        placeholder="Description"
        value={form.description}
        onChange={onChange}
        required
        disabled={loading}
      />
      <button type="submit" disabled={loading} className="flex items-center gap-2">
        {loading ? <ClipLoader size={20} color="#fff" /> : 'Add Expense'}
      </button>
      {error && <p className="expenses-error">{error}</p>}
    </form>
  );
}

AddExpenseForm.propTypes = {
  form: PropTypes.object.isRequired,
  onChange: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  loading: PropTypes.bool,
  error: PropTypes.string,
};

export default AddExpenseForm;
