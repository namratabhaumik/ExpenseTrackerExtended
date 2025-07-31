import React, { useState, useEffect, useRef, useCallback } from 'react';
import PropTypes from 'prop-types';
import { toast } from 'react-toastify';
import axios from 'axios';
import ModalBackdrop from './ModalBackdrop';
import { Spinner } from 'react-bootstrap';
import './DeleteExpenseDialog.css';

// Utility function to ensure modal stays within viewport
const getAdjustedPosition = (x, y, width = 400, height = 300) => {
  const viewportWidth = window.innerWidth;
  const viewportHeight = window.innerHeight;
  
  // Adjust x position if modal would go off the right edge
  let adjustedX = x;
  if (x + width > viewportWidth) {
    adjustedX = viewportWidth - width - 20; // 20px padding from edge
  }
  
  // Adjust y position if modal would go off the bottom
  let adjustedY = y;
  if (y + height > viewportHeight) {
    adjustedY = viewportHeight - height - 20; // 20px padding from edge
  }
  
  return { x: Math.max(20, adjustedX), y: Math.max(20, adjustedY) };
};

function EditExpenseModal({ show, handleClose, expense, position, onExpenseUpdated, userCategories = [] }) {
  const [form, setForm] = useState({
    amount: '',
    category: '',
    description: '',
  });
  const [loading, setLoading] = useState(false);
  const modalRef = useRef(null);
  const [modalStyle, setModalStyle] = useState({});
  
  // Update modal position when show or position changes
  useEffect(() => {
    if (show && position) {
      // Adjust position to keep modal within viewport
      const adjustedPos = getAdjustedPosition(position.x, position.y, 400, 300);
      setModalStyle({
        position: 'absolute',
        left: `${adjustedPos.x}px`,
        top: `${adjustedPos.y}px`,
        maxHeight: '90vh',
        overflowY: 'auto',
        zIndex: 1050,
        width: '400px',
        maxWidth: '90vw',
      });
    }
  }, [show, position]);

  // Initialize form state when modal opens or expense changes
  useEffect(() => {
    if (show && expense) {
      setForm({
        amount: expense.amount || '',
        category: expense.category || '',
        description: expense.description || '',
      });
    }
  }, [show, expense]);
  
  // Get unique categories from user's expenses
  const uniqueCategories = React.useMemo(() => {
    return [...new Set(userCategories)].sort();
  }, [userCategories]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    if (!expense?.id) {
      toast.error('Invalid expense data. Please try again.');
      return;
    }
    
    setLoading(true);
    try {
      const response = await axios.put(
        `${process.env.REACT_APP_BACKEND_URL}/api/expenses/${expense.id}/`,
        form,
        {
          headers: { 'Content-Type': 'application/json' },
          withCredentials: true,
        },
      );
      
      // Check if the response contains the updated expense data
      const updatedExpense = response.data.expense || response.data;
      
      if (updatedExpense) {
        toast.success('Expense updated successfully!', {
          position: 'top-right',
          style: {
            background: '#d1fae5',
            color: '#2563EB',
            borderRadius: 8,
            fontWeight: 500,
          },
          progressStyle: { background: '#10b981' },
        });
        
        // Call the onExpenseUpdated callback with the updated expense data
        if (onExpenseUpdated) {
          onExpenseUpdated(updatedExpense);
        }
        
        // Close the modal after a short delay to allow the UI to update
        setTimeout(() => {
          handleClose();
        }, 100);
      }
    } catch (error) {
      const errMsg = (error.response && 
        (error.response.data?.error || error.response.data?.message)) || 
        error.message || 
        'Failed to update expense';
      
      toast.error(errMsg, {
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
  }, [expense, form, handleClose, onExpenseUpdated]);

  // Handle keyboard events for accessibility
  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Escape' && !loading) {
      handleClose();
    }
  }, [handleClose, loading]);

  if (!show) return null;

  return (
    <ModalBackdrop 
      show={show} 
      onClose={!loading ? handleClose : undefined}
      onKeyDown={(e) => e.key === 'Escape' && !loading && handleClose()}
    >
      <div className="fixed inset-0 flex items-center justify-center z-50">
        <div
          ref={modalRef}
          className="relative w-full max-w-md mx-4 bg-white dark:bg-gray-800 rounded-lg shadow-xl overflow-hidden modal-light-bg"
          role="dialog"
          aria-modal="true"
          aria-labelledby="edit-expense-title"
          tabIndex={-1}
        >
          <div className="w-full">
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white modal-light-bg">
              <h3 id="edit-expense-title" className="text-lg font-medium text-gray-900 dark:text-white">
                <i className="fas fa-edit text-teal-500 mr-2"></i>
                Edit Expense
              </h3>
              <button
                type="button"
                onClick={!loading ? handleClose : undefined}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') handleClose();
                }}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
                disabled={loading}
                aria-label="Close dialog"
              >
                <span className="sr-only">Close</span>
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        
          <div className="p-6 bg-white dark:bg-gray-800 text-gray-900 dark:text-white modal-light-bg">
            <form onSubmit={handleSubmit}>
              <div className="space-y-4 text-gray-900 dark:text-gray-300">
                <div>
                  <label htmlFor="amount" className="block text-sm font-medium text-gray-900 dark:text-gray-300 mb-1">
                    Amount
                  </label>
                  <input
                    type="number"
                    id="amount"
                    name="amount"
                    value={form.amount}
                    onChange={handleChange}
                    step="0.01"
                    min="0.01"
                    required
                    className="w-full px-3 py-2 text-base border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 dark:bg-gray-700 dark:text-white"
                    disabled={loading}
                  />
                </div>

                <div>
                  <label htmlFor="category" className="block text-sm font-medium text-gray-900 dark:text-gray-300 mb-1">
                    Category
                  </label>
                  <select
                    id="category"
                    name="category"
                    value={form.category}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 text-base border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 dark:bg-gray-700 dark:text-white"
                    disabled={loading}
                  >
                    <option value="">Select a category</option>
                    {uniqueCategories.length > 0 ? (
                      uniqueCategories.map((cat) => (
                        <option key={cat} value={cat} className="hover:bg-teal-100 dark:hover:bg-teal-900">
                          {cat}
                        </option>
                      ))
                    ) : (
                      [
                        'Food', 'Transportation', 'Housing', 'Utilities',
                        'Entertainment', 'Shopping', 'Healthcare', 'Other',
                      ].map((cat) => (
                        <option key={cat} value={cat} className="hover:bg-teal-100 dark:hover:bg-teal-900">
                          {cat}
                        </option>
                      ))
                    )}
                  </select>
                </div>
                
                <div>
                  <label htmlFor="description" className="block text-sm font-medium text-gray-900 dark:text-gray-300 mb-1">
                    Description
                  </label>
                  <textarea
                    id="description"
                    name="description"
                    rows={3}
                    value={form.description}
                    onChange={handleChange}
                    className="w-full px-3 py-2 text-base border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 dark:bg-gray-700 dark:text-white"
                    disabled={loading}
                  />
                </div>
              </div>
              
              <div className="px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse border-t border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800 modal-light-bg mt-6 -mx-6 -mb-6">
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-teal-600 text-base font-medium !text-white hover:bg-teal-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed dark:bg-teal-600 dark:hover:bg-teal-700 dark:focus:ring-teal-500 dark:focus:ring-offset-2 dark:!text-white"
                  style={{ cursor: 'pointer !important' }}
                >
                  {loading ? (
                    <span className="flex items-center">
                      <Spinner
                        as="span"
                        animation="border"
                        size="sm"
                        role="status"
                        aria-hidden="true"
                        className="mr-2"
                      />
                      <span>Updating...</span>
                    </span>
                  ) : (
                    'Update Expense'
                  )}
                </button>
                <button
                  type="button"
                  onClick={handleClose}
                  disabled={loading}
                  className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:hover:bg-gray-600"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </ModalBackdrop>
  );
}

EditExpenseModal.propTypes = {
  show: PropTypes.bool.isRequired,
  handleClose: PropTypes.func.isRequired,
  userCategories: PropTypes.arrayOf(PropTypes.string),
  expense: PropTypes.shape({
    id: PropTypes.string.isRequired,
    amount: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.number,
    ]).isRequired,
    category: PropTypes.string.isRequired,
    description: PropTypes.string,
    timestamp: PropTypes.string,
  }),
  position: PropTypes.shape({
    x: PropTypes.number.isRequired,
    y: PropTypes.number.isRequired,
  }),
  onExpenseUpdated: PropTypes.func,
};

EditExpenseModal.defaultProps = {
  expense: null,
  onExpenseUpdated: () => {},
  userCategories: [],
};

export default EditExpenseModal;
