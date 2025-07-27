import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import Expenses from './Expenses';

// Mock axios
jest.mock('axios');

describe('Expenses Component', () => {
  const mockSetDashboardRefreshFlag = jest.fn();
  
  const renderExpenses = () => {
    return render(
      <Expenses 
        setDashboardRefreshFlag={mockSetDashboardRefreshFlag} 
      />,
    );
  };

  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  test('renders loading state initially', async () => {
    // Mock axios.get to never resolve, keeping loading state true
    axios.get.mockImplementationOnce(() => new Promise(() => {}));
    
    renderExpenses();
    
    // Check for loading state
    expect(screen.getByText(/Loading.../i)).toBeInTheDocument();
  });

  test('renders error state when API call fails', async () => {
    // Mock a failed API call
    axios.get.mockRejectedValueOnce({
      response: {
        data: { error: 'Failed to fetch expenses' },
      },
    });

    renderExpenses();
    
    // Wait for error message to appear
    await waitFor(() => {
      expect(screen.getAllByText(/Failed to fetch expenses/i)[0]).toBeInTheDocument();
    });
  });

  test('renders expense form and table when data loads', async () => {
    // Mock successful API response
    axios.get.mockResolvedValueOnce({
      data: { 
        expenses: [
          {
            id: '1',
            amount: '10.50',
            category: 'Food',
            description: 'Lunch',
            timestamp: new Date().toISOString(),
          },
        ], 
      },
    });

    renderExpenses();
    
    // Check that form inputs are rendered
    expect(screen.getByPlaceholderText('Amount')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Category')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Description')).toBeInTheDocument();
    
    // Check that the table is rendered with data
    await waitFor(() => {
      expect(screen.getByRole('table')).toBeInTheDocument();
    });
    
    await waitFor(() => {
      expect(screen.getByText('Food')).toBeInTheDocument();
    });
    
    await waitFor(() => {
      expect(screen.getByText('Lunch')).toBeInTheDocument();
    });
  });
});
