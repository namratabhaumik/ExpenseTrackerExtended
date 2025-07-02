import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Expenses from './Expenses';

// Mock axios for API calls
jest.mock('axios', () => ({
  post: jest.fn(),
  get: jest.fn(),
}));

describe('Expenses Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders expense form and list', () => {
    render(<Expenses />);
    expect(screen.getByLabelText(/Amount/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Category/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Description/i)).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /add expense/i }),
    ).toBeInTheDocument();
    expect(screen.getByText(/Expenses List/i)).toBeInTheDocument();
  });

  test('adds new expense successfully', async () => {
    render(<Expenses />);
    fireEvent.change(screen.getByLabelText(/Amount/i), {
      target: { value: '50.00' },
    });
    fireEvent.change(screen.getByLabelText(/Category/i), {
      target: { value: 'Entertainment' },
    });
    fireEvent.change(screen.getByLabelText(/Description/i), {
      target: { value: 'Movie tickets' },
    });
    fireEvent.click(screen.getByRole('button', { name: /add expense/i }));
    await waitFor(() => {
      expect(
        screen.getByText(/Expense added successfully/i),
      ).toBeInTheDocument();
    });
  });

  test('validates required fields when adding expense', async () => {
    render(<Expenses />);
    fireEvent.click(screen.getByRole('button', { name: /add expense/i }));
    await waitFor(() => {
      expect(screen.getByText(/Amount is required/i)).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(screen.getByText(/Category is required/i)).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(screen.getByText(/Description is required/i)).toBeInTheDocument();
    });
  });

  test('validates amount format', async () => {
    render(<Expenses />);
    fireEvent.change(screen.getByLabelText(/Amount/i), {
      target: { value: 'invalid-amount' },
    });
    fireEvent.change(screen.getByLabelText(/Category/i), {
      target: { value: 'Food' },
    });
    fireEvent.change(screen.getByLabelText(/Description/i), {
      target: { value: 'Lunch' },
    });
    fireEvent.click(screen.getByRole('button', { name: /add expense/i }));
    await waitFor(() => {
      expect(
        screen.getByText(/Please enter a valid amount/i),
      ).toBeInTheDocument();
    });
  });

  test('displays expenses list', () => {
    render(<Expenses />);
    const expensesList = screen.getByTestId('expenses-list');
    expect(expensesList).toBeInTheDocument();
  });

  test('shows loading state when fetching expenses', async () => {
    render(<Expenses />);
    expect(screen.getByText(/Loading expenses/i)).toBeInTheDocument();
  });

  test('handles error when fetching expenses', async () => {
    render(<Expenses />);
    await waitFor(() => {
      expect(screen.getByText(/Error loading expenses/i)).toBeInTheDocument();
    });
  });

  test('filters expenses by category', () => {
    render(<Expenses />);
    fireEvent.change(screen.getByLabelText(/Filter by category/i), {
      target: { value: 'Food' },
    });
    expect(screen.getByText(/Filtered by: Food/i)).toBeInTheDocument();
  });

  test('sorts expenses by amount', () => {
    render(<Expenses />);
    fireEvent.click(screen.getByRole('button', { name: /sort by amount/i }));
    expect(
      screen.getByRole('button', { name: /sorted by amount/i }),
    ).toBeInTheDocument();
  });
});
