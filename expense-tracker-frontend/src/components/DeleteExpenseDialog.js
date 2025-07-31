import React, { useState, useCallback, useEffect, useRef } from 'react';
import ModalBackdrop from './ModalBackdrop';
import PropTypes from 'prop-types';
import { Spinner } from 'react-bootstrap';
import { toast } from 'react-toastify';
import axios from 'axios';
import 'react-toastify/dist/ReactToastify.css';
import './DeleteExpenseDialog.css';

/**
 * DeleteExpenseDialog component.
 * 
 * @param {Object} props - Component props.
 * @param {Boolean} props.show - Whether the dialog is shown.
 * @param {Function} props.handleClose - Function to close the dialog.
 * @param {Object} props.expense - Expense object to delete.
 * @param {Function} props.onExpenseDeleted - Callback function when expense is deleted.
 */
function DeleteExpenseDialog({ show, handleClose, expense, onExpenseDeleted }) {
  const [loading, setLoading] = useState(false);
  const [, setError] = useState('');
  const modalRef = useRef(null);

  // Handle keyboard events for the dialog
  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Escape' && !loading) {
      handleClose();
    }
  }, [loading, handleClose]);

  // Set up keyboard trap for accessibility
  useEffect(() => {
    if (!show) return;

    const focusableSelector = 'button, [href], input, select, textarea, ' +
      '[tabindex]:not([tabindex="-1"])';
    
    const handleTabKey = (e) => {
      if (e.key !== 'Tab') return;

      const elements = modalRef.current?.querySelectorAll(focusableSelector);
      if (!elements?.length) return;

      const firstElement = elements[0];
      const lastElement = elements[elements.length - 1];
      const activeElement = document.activeElement;

      if (e.shiftKey && activeElement === firstElement) {
        lastElement.focus();
        e.preventDefault();
      } else if (!e.shiftKey && activeElement === lastElement) {
        firstElement.focus();
        e.preventDefault();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keydown', handleTabKey);

    // Focus the first element when modal opens
    const firstFocusable = modalRef.current?.querySelector(
      'button:not([disabled])',
    );
    firstFocusable?.focus();

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('keydown', handleTabKey);
    };
  }, [show, handleKeyDown]);



  // Handle delete expense
  const handleDelete = async () => {
    if (!expense?.id) return;
    
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.delete(
        `${process.env.REACT_APP_BACKEND_URL}/api/expenses/${expense.id}/`,
        { withCredentials: true },
      );
      
      if (response.status === 200 || response.status === 204) {
        toast.success('Expense deleted successfully!');
        onExpenseDeleted?.(expense);
        handleClose();
      } else {
        throw new Error('Failed to delete expense');
      }
    } catch (err) {
      // Log error to console in development
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error deleting expense:', err);
      }
      const errorMsg = err.response?.data?.error || 
        'Failed to delete expense. Please try again.';
      setError(errorMsg);
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  // Safely access expense properties
  const safeExpense = expense || {};

  const amount = safeExpense.amount && typeof safeExpense.amount === 'string' 
    ? parseFloat(safeExpense.amount) 
    : Number(safeExpense.amount) || 0;
  
  // Early return after all hooks
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
          aria-labelledby="delete-dialog-title"
          aria-describedby="delete-dialog-description"
          tabIndex={-1}
        >
          <div className="w-full">
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white modal-light-bg">
              <h3 id="delete-dialog-title" className="text-lg font-medium text-gray-900 dark:text-white">
                <i className="fas fa-trash-alt text-red-500 mr-2"></i>
                Delete Expense
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
            <p id="delete-dialog-description" className="text-sm text-gray-900 dark:text-gray-300 mb-6">
            Are you sure you want to delete this expense? This action cannot be undone.
            </p>
          
            <div className="space-y-4 text-gray-900 dark:text-gray-300">
              <div className="flex">
                <span className="font-medium w-24">Amount:</span>
                <span className="font-semibold">
                ${amount.toFixed(2)}
                </span>
              </div>
            
              <div className="flex">
                <span className="w-24">Category:</span>
                <span>{safeExpense.category || 'N/A'}</span>
              </div>
            
              <div className="flex items-start">
                <span className="w-24">
                  Description:
                </span>
                <span className="flex-1 text-left">
                  {safeExpense.description || 'No description'}
                </span>
              </div>
            </div>
          </div>
        
          <div className="px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse border-t border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800 modal-light-bg">
            <button
              type="button"
              onClick={handleDelete}
              disabled={loading}
              className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Delete expense"
            >
              {loading ? (
                <>
                  <Spinner
                    as="span"
                    animation="border"
                    size="sm"
                    role="status"
                    aria-hidden="true"
                    className="mr-2"
                  />
                  <span aria-live="polite">Deleting...</span>
                </>
              ) : (
                'Delete'
              )}
            </button>
            <button
              type="button"
              onClick={handleClose}
              disabled={loading}
              className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2
              bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2
              focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50
              disabled:cursor-not-allowed dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:hover:bg-gray-600"
              aria-label="Cancel deleting expense"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </ModalBackdrop>
  );
}

DeleteExpenseDialog.propTypes = {
  show: PropTypes.bool.isRequired,
  handleClose: PropTypes.func.isRequired,
  expense: PropTypes.shape({
    id: PropTypes.string.isRequired,
    amount: PropTypes.number.isRequired,
    category: PropTypes.string.isRequired,
    description: PropTypes.string,
  }).isRequired,
  onExpenseDeleted: PropTypes.func,
};

export default DeleteExpenseDialog;
