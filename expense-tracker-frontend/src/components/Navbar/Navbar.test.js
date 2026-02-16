import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Navbar from './Navbar';

describe('Navbar', () => {
  const noop = jest.fn();

  test('renders fallback nav when `fallback` is true', () => {
    render(
      <Navbar
        onLogout={noop}
        onNavigate={noop}
        activePage="dashboard"
        theme="light"
        onThemeToggle={noop}
        fallback
      />,
    );

    expect(screen.getByText('ExpenseTrackerExtended')).toBeInTheDocument();
    expect(screen.getAllByRole('button', { name: /Navigate to/i }).length).toBeGreaterThan(0);
    expect(screen.getByRole('button', { name: /Logout/i })).toBeInTheDocument();
  });

  test('calls onNavigate / onLogout / onThemeToggle and keyboard handlers', () => {
    const onNavigate = jest.fn();
    const onLogout = jest.fn();
    const onThemeToggle = jest.fn();

    render(
      <Navbar
        onLogout={onLogout}
        onNavigate={onNavigate}
        activePage="expenses"
        theme="dark"
        onThemeToggle={onThemeToggle}
      />,
    );

    // Brand navigation (click the brand text)
    fireEvent.click(screen.getByText('ExpenseTrackerExtended'));
    expect(onNavigate).toHaveBeenCalledWith('dashboard');

    // Click an internal nav link (Expenses)
    fireEvent.click(screen.getByLabelText('Navigate to Expenses'));
    expect(onNavigate).toHaveBeenCalledWith('expenses');

    // Theme toggle
    fireEvent.click(screen.getByLabelText(/Switch to/i));
    expect(onThemeToggle).toHaveBeenCalled();

    // Logout
    fireEvent.click(screen.getByLabelText('Logout'));
    expect(onLogout).toHaveBeenCalled();

    // Keyboard: simulate Enter on brand
    fireEvent.keyDown(screen.getByText('ExpenseTrackerExtended'), { key: 'Enter' });
    expect(onNavigate).toHaveBeenCalled();
  });

  test('mobile menu opens and closes', () => {
    render(
      <Navbar
        onLogout={noop}
        onNavigate={noop}
        activePage="dashboard"
        theme="light"
        onThemeToggle={noop}
      />,
    );

    // Open mobile menu (hamburger)
    const openBtn = screen.getByLabelText('Open menu');
    fireEvent.click(openBtn);

    // Mobile menu (dialog) should appear
    expect(screen.getByRole('dialog')).toBeInTheDocument();

    // Close the menu
    const closeBtn = screen.getByLabelText('Close menu');
    fireEvent.click(closeBtn);
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });
});
