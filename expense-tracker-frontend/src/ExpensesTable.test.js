import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ExpensesTable from './ExpensesTable';

describe('ExpensesTable component', () => {
  const sampleExpenses = [
    {
      id: '1',
      amount: 10.5,
      category: 'Food',
      description: 'Lunch',
      timestamp: Date.now(),
    },
    {
      id: '2',
      amount: 25,
      category: 'Transport',
      description: 'Cab',
      timestamp: Date.now(),
    },
  ];

  test('shows loading state', () => {
    render(<ExpensesTable expenses={[]} loading />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test('shows empty state message when no expenses', () => {
    render(<ExpensesTable expenses={[]} />);
    expect(screen.getByText(/no expenses found/i)).toBeInTheDocument();
  });

  test('renders rows for each expense', () => {
    render(<ExpensesTable expenses={sampleExpenses} />);

    // Amount cells formatted with $ and 2 decimals
    expect(screen.getByText('$10.50')).toBeInTheDocument();
    expect(screen.getByText('$25.00')).toBeInTheDocument();

    // Category cells
    expect(screen.getByText('Food')).toBeInTheDocument();
    expect(screen.getByText('Transport')).toBeInTheDocument();

    // Description cells
    expect(screen.getByText('Lunch')).toBeInTheDocument();
    expect(screen.getByText('Cab')).toBeInTheDocument();
  });
});
