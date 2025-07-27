import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import AddExpenseForm from './AddExpenseForm';

// Mock ClipLoader to avoid SVG/CSS warnings in Jest DOM
jest.mock('react-spinners', () => ({
  ClipLoader: () => <span data-testid="clip-loader" />,
}));

describe('AddExpenseForm component', () => {
  const defaultForm = {
    amount: '12.50',
    category: 'Food',
    description: 'Lunch',
  };

  test('renders all input fields with provided values', () => {
    render(
      <AddExpenseForm
        form={defaultForm}
        onChange={jest.fn()}
        onSubmit={jest.fn()}
      />,
    );

    expect(screen.getByPlaceholderText('Amount')).toHaveValue(+defaultForm.amount);
    expect(screen.getByPlaceholderText('Category')).toHaveValue(defaultForm.category);
    expect(screen.getByPlaceholderText('Description')).toHaveValue(defaultForm.description);
  });

  test('calls onChange when input values change', () => {
    const handleChange = jest.fn();
    render(
      <AddExpenseForm form={defaultForm} onChange={handleChange} onSubmit={jest.fn()} />,
    );
    const amountInput = screen.getByPlaceholderText('Amount');
    fireEvent.change(amountInput, { target: { value: '20.00' } });
    expect(handleChange).toHaveBeenCalledTimes(1);
  });

  test('calls onSubmit when form is submitted', () => {
    const handleSubmit = jest.fn((e) => e.preventDefault());
    render(
      <AddExpenseForm form={defaultForm} onChange={jest.fn()} onSubmit={handleSubmit} />,
    );
    fireEvent.submit(screen.getByRole('button', { name: /add expense/i }));
    expect(handleSubmit).toHaveBeenCalledTimes(1);
  });

  test('disables inputs and shows loader when loading', () => {
    render(
      <AddExpenseForm
        form={defaultForm}
        onChange={jest.fn()}
        onSubmit={jest.fn()}
        loading
      />,
    );
    expect(screen.getByPlaceholderText('Amount')).toBeDisabled();
    expect(screen.getByPlaceholderText('Category')).toBeDisabled();
    expect(screen.getByPlaceholderText('Description')).toBeDisabled();
    expect(screen.getByTestId('clip-loader')).toBeInTheDocument();
  });

  test('displays error message when error prop provided', () => {
    const errorMessage = 'Something went wrong';
    render(
      <AddExpenseForm
        form={defaultForm}
        onChange={jest.fn()}
        onSubmit={jest.fn()}
        error={errorMessage}
      />,
    );
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });
});
