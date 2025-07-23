import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Profile from './Profile';

// Use Jest mock functions for toast
export const mockToastSuccess = jest.fn();
export const mockToastError = jest.fn();
jest.mock('react-toastify', () => ({
  toast: {
    success: (...args) => mockToastSuccess(...args),
    error: (...args) => mockToastError(...args),
  },
  ToastContainer: () => <div />,
}));

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';
const TEST_THEME = 'light';

describe('Profile component', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
    mockToastSuccess.mockClear();
    mockToastError.mockClear();
  });
  afterEach(() => {
    jest.resetAllMocks();
  });

  it('fetches and displays user info', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        profile: { name: 'Test User', email: 'test@example.com' },
      }),
    });

    render(<Profile theme={TEST_THEME} />);

    // Check that fetch was called correctly for cookie-based auth
    expect(fetch).toHaveBeenCalledWith(`${API_BASE}/api/profile/`, {
      credentials: 'include',
    });

    // Wait for the user's name to appear, which confirms the fetch and state update are complete
    expect(await screen.findByText('Test User')).toBeInTheDocument();
    expect(screen.getByText('test@example.com')).toBeInTheDocument();
  });

  it('allows editing and saving profile info', async () => {
    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          profile: { name: 'Test User', email: 'test@example.com' },
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          message: 'Profile updated successfully!',
          status: 'success',
        }),
      });
    render(<Profile theme={TEST_THEME} />);
    await screen.findByText('Test User');
    fireEvent.click(screen.getByText(/edit profile/i));
    fireEvent.change(screen.getByLabelText(/name/i), {
      target: { value: 'New Name' },
    });
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'new@example.com' },
    });
    fireEvent.click(screen.getByText(/^save$/i));
    await waitFor(() =>
      expect(fetch).toHaveBeenCalledWith(
        `${API_BASE}/api/profile/`,
        expect.objectContaining({ method: 'PUT' }),
      ),
    );
    await waitFor(() => {
      expect(screen.getByText('New Name')).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(screen.getByText('new@example.com')).toBeInTheDocument();
    });
  });

  it('shows validation error for invalid email', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        profile: { name: 'Test User', email: 'test@example.com' },
      }),
    });
    render(<Profile theme={TEST_THEME} />);
    await screen.findByText('Test User');
    fireEvent.click(screen.getByText(/edit profile/i));
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'invalid-email' },
    });
    fireEvent.click(screen.getByText(/^save$/i));
    // Assert on mockToastError for error
    await waitFor(() => {
      expect(mockToastError).toHaveBeenCalledWith(
        expect.stringMatching(/invalid email format/i),
        expect.anything(),
      );
    });
  });

  it('handles API error on profile fetch', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ error: 'Failed to fetch profile' }),
    });
    render(<Profile theme={TEST_THEME} />);
    expect(
      await screen.findByText(/failed to fetch profile/i),
    ).toBeInTheDocument();
  });

  it('allows password change and shows success', async () => {
    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          profile: { name: 'Test User', email: 'test@example.com' },
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          message: 'Password changed successfully!',
          status: 'success',
        }),
      });
    render(<Profile theme={TEST_THEME} />);
    await screen.findByText('Test User');
    fireEvent.change(screen.getByLabelText(/current password/i), {
      target: { value: 'oldPass123!' },
    });
    fireEvent.change(screen.getByLabelText(/^new password$/i), {
      target: { value: 'NewPass123!' },
    });
    fireEvent.change(screen.getByLabelText(/confirm new password/i), {
      target: { value: 'NewPass123!' },
    });
    fireEvent.click(screen.getByRole('button', { name: /change password/i }));
    await waitFor(() =>
      expect(fetch).toHaveBeenCalledWith(
        `${API_BASE}/api/profile/change-password/`,
        expect.objectContaining({ method: 'POST' }),
      ),
    );
    await waitFor(() => {
      expect(screen.getByLabelText(/current password/i)).toHaveValue('');
    });
    await waitFor(() => {
      expect(screen.getByLabelText(/^new password$/i)).toHaveValue('');
    });
    await waitFor(() => {
      expect(screen.getByLabelText(/confirm new password/i)).toHaveValue('');
    });
  });

  it('shows error if new passwords do not match', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        profile: { name: 'Test User', email: 'test@example.com' },
      }),
    });
    render(<Profile theme={TEST_THEME} />);
    await screen.findByText('Test User');
    fireEvent.change(screen.getByLabelText(/current password/i), {
      target: { value: 'oldPass123!' },
    });
    fireEvent.change(screen.getByLabelText(/^new password$/i), {
      target: { value: 'NewPass123!' },
    });
    fireEvent.change(screen.getByLabelText(/confirm new password/i), {
      target: { value: 'DifferentPass!' },
    });
    fireEvent.click(screen.getByRole('button', { name: /change password/i }));
    // Instead of toast, check for error in DOM
    await waitFor(() => {
      expect(screen.getAllByText(/do not match/i).length).toBeGreaterThan(0);
    });
  });

  it('shows error if password does not meet requirements', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        profile: { name: 'Test User', email: 'test@example.com' },
      }),
    });
    render(<Profile theme={TEST_THEME} />);
    await screen.findByText('Test User');
    fireEvent.change(screen.getByLabelText(/current password/i), {
      target: { value: 'oldPass123!' },
    });
    fireEvent.change(screen.getByLabelText(/^new password$/i), {
      target: { value: 'short' },
    });
    fireEvent.change(screen.getByLabelText(/confirm new password/i), {
      target: { value: 'short' },
    });
    fireEvent.click(screen.getByRole('button', { name: /change password/i }));
    // Instead of toast, check for error in DOM
    await waitFor(() => {
      expect(
        screen.getByText(/does not meet requirements/i),
      ).toBeInTheDocument();
    });
  });

  it('handles API error on password change', async () => {
    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          profile: { name: 'Test User', email: 'test@example.com' },
        }),
      })
      .mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Failed to change password' }),
      });
    render(<Profile theme={TEST_THEME} />);
    await screen.findByText('Test User');
    fireEvent.change(screen.getByLabelText(/current password/i), {
      target: { value: 'oldPass123!' },
    });
    fireEvent.change(screen.getByLabelText(/^new password$/i), {
      target: { value: 'NewPass123!' },
    });
    fireEvent.change(screen.getByLabelText(/confirm new password/i), {
      target: { value: 'NewPass123!' },
    });
    fireEvent.click(screen.getByRole('button', { name: /change password/i }));
    // Assert on mockToastError for error
    await waitFor(() => {
      expect(mockToastError).toHaveBeenCalledWith(
        expect.stringMatching(/failed to change password/i),
        expect.anything(),
      );
    });
  });
});
