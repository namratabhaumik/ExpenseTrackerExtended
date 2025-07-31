import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Modal, Button, Form } from 'react-bootstrap';
import { toast } from 'react-toastify';
import axios from 'axios';

function EditExpenseModal({ show, handleClose, expense, onExpenseUpdated }) {
  const [form, setForm] = useState({
    amount: '',
    category: '',
    description: '',
  });
  const [loading, setLoading] = useState(false);

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

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
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
      
      if (response.data.status === 'success') {
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
        
        // Close modal and refresh expenses
        handleClose();
        if (onExpenseUpdated) {
          onExpenseUpdated(response.data.expense);
        }
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
  };

  return (
    <Modal show={show} onHide={handleClose}>
      <Modal.Header closeButton>
        <Modal.Title>Edit Expense</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form onSubmit={handleSubmit}>
          <Form.Group controlId="amount">
            <Form.Label>Amount</Form.Label>
            <Form.Control
              type="number"
              step="0.01"
              name="amount"
              value={form.amount}
              onChange={handleChange}
              required
              min="0"
            />
          </Form.Group>
          <Form.Group controlId="category">
            <Form.Label>Category</Form.Label>
            <Form.Control
              type="text"
              name="category"
              value={form.category}
              onChange={handleChange}
              required
            />
          </Form.Group>
          <Form.Group controlId="description">
            <Form.Label>Description</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              name="description"
              value={form.description}
              onChange={handleChange}
            />
          </Form.Group>
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        <Button type="submit" variant="primary" onClick={handleSubmit} disabled={loading}>
          {loading ? 'Updating...' : 'Update'}
        </Button>
      </Modal.Footer>
    </Modal>
  );
}

EditExpenseModal.propTypes = {
  show: PropTypes.bool.isRequired,
  handleClose: PropTypes.func.isRequired,
  expense: PropTypes.shape({
    id: PropTypes.string.isRequired,
    amount: PropTypes.number.isRequired,
    category: PropTypes.string.isRequired,
    description: PropTypes.string,
  }).isRequired,
  onExpenseUpdated: PropTypes.func,
};

export default EditExpenseModal;
