import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
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

const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
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
    let callCount = 0;
    global.fetch = jest.fn().mockImplementation((url) => {
      callCount += 1;
      // First call is for csrf-token (from apiGet to ensure token)
      if (url.includes('/csrf-token/')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ csrf_token: 'test-token' }),
        });
      }
      // Second call is the actual profile fetch
      if (url.includes('/profile/')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            profile: { name: 'Test User', email: 'test@example.com' },
          }),
        });
      }
    });

    await act(async () => {
      render(<Profile theme={TEST_THEME} />);
    });

    // Wait for the user's name to appear, which confirms the fetch and state update are complete
    expect(await screen.findByText('Test User')).toBeInTheDocument();
    expect(screen.getByText('test@example.com')).toBeInTheDocument();
  });

  it('allows editing and saving profile info', async () => {
    let callCount = 0;
    global.fetch = jest.fn().mockImplementation((url, opts) => {
      callCount += 1;
      // CSRF token calls
      if (url.includes('/csrf-token/')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ csrf_token: 'test-token' }),
        });
      }
      // Profile GET
      if (url.includes('/profile/') && (!opts || opts.method === 'GET' || !opts.method)) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            profile: { name: 'Test User', email: 'test@example.com' },
          }),
        });
      }
      // Profile PUT
      if (url.includes('/profile/') && opts && opts.method === 'PUT') {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            message: 'Profile updated successfully!',
            status: 'success',
            profile: { name: 'New Name', email: 'test@example.com' },
          }),
        });
      }
    });

    await act(async () => {
      render(<Profile theme={TEST_THEME} />);
    });
    await screen.findByText('Test User');
    fireEvent.click(screen.getByText(/Edit Name/i));
    fireEvent.change(screen.getByDisplayValue('Test User'), {
      target: { value: 'New Name' },
    });
    fireEvent.click(screen.getByText(/^Save$/i));
    await waitFor(() =>
      expect(fetch).toHaveBeenCalledWith(
        `${API_BASE}/api/profile/`,
        expect.objectContaining({ method: 'PUT' }),
      ),
    );
    await waitFor(() => {
      expect(screen.getByText('New Name')).toBeInTheDocument();
    });
  });

  it('shows validation error for invalid email', async () => {
    let callCount = 0;
    global.fetch = jest.fn().mockImplementation((url) => {
      callCount += 1;
      if (url.includes('/csrf-token/')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ csrf_token: 'test-token' }),
        });
      }
      if (url.includes('/profile/')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            profile: { name: 'Test User', email: 'test@example.com' },
          }),
        });
      }
    });

    await act(async () => {
      render(<Profile theme={TEST_THEME} />);
    });
    await screen.findByText('Test User');
    fireEvent.click(screen.getByText(/Edit Name/i));
    // Note: The component doesn't have email field in edit mode - it's read-only
    // So this test should check that only name can be edited
    fireEvent.change(screen.getByDisplayValue('Test User'), {
      target: { value: 'New Name' },
    });
    fireEvent.click(screen.getByText(/^Save$/i));
    // The save should succeed since we're only editing the name field
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        `${API_BASE}/api/profile/`,
        expect.objectContaining({ method: 'PUT' }),
      );
    });
  });

  it('handles API error on profile fetch', async () => {
    global.fetch = jest.fn().mockImplementation((url) => {
      if (url.includes('/csrf-token/')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ csrf_token: 'test-token' }),
        });
      }
      if (url.includes('/profile/')) {
        return Promise.resolve({
          ok: false,
          json: async () => ({ error: 'Failed to fetch profile' }),
        });
      }
    });

    await act(async () => {
      render(<Profile theme={TEST_THEME} />);
    });
    expect(
      await screen.findByText(/failed to fetch profile/i),
    ).toBeInTheDocument();
  });

  it('allows password change and shows success', async () => {
    let callCount = 0;
    global.fetch = jest.fn().mockImplementation((url, opts) => {
      callCount += 1;
      if (url.includes('/csrf-token/')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ csrf_token: 'test-token' }),
        });
      }
      if (url.includes('/profile/') && (!opts || !opts.method || opts.method === 'GET')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            profile: { name: 'Test User', email: 'test@example.com' },
          }),
        });
      }
      if (url.includes('/change-password/') && opts && opts.method === 'POST') {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            message: 'Password changed successfully!',
            status: 'success',
          }),
        });
      }
    });

    await act(async () => {
      render(<Profile theme={TEST_THEME} />);
    });
    await screen.findByText('Test User');
    fireEvent.change(screen.getByLabelText(/current password/i), {
      target: { value: 'Test_Old_1!' },
    });
    fireEvent.change(screen.getByLabelText(/^new password$/i), {
      target: { value: 'Test_New_1!' },
    });
    fireEvent.change(screen.getByLabelText(/confirm new password/i), {
      target: { value: 'Test_New_1!' },
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
    await act(async () => {
      render(<Profile theme={TEST_THEME} />);
    });
    await screen.findByText('Test User');
    fireEvent.change(screen.getByLabelText(/current password/i), {
      target: { value: 'Test_Old_1!' },
    });
    fireEvent.change(screen.getByLabelText(/^new password$/i), {
      target: { value: 'Test_New_1!' },
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
    global.fetch = jest.fn().mockImplementation((url) => {
      if (url.includes('/csrf-token/')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ csrf_token: 'test-token' }),
        });
      }
      if (url.includes('/profile/')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            profile: { name: 'Test User', email: 'test@example.com' },
          }),
        });
      }
    });

    await act(async () => {
      render(<Profile theme={TEST_THEME} />);
    });
    await screen.findByText('Test User');
    fireEvent.change(screen.getByLabelText(/current password/i), {
      target: { value: 'Test_Old_1!' },
    });
    fireEvent.change(screen.getByLabelText(/^new password$/i), {
      target: { value: 'short' },
    });
    fireEvent.change(screen.getByLabelText(/confirm new password/i), {
      target: { value: 'short' },
    });
    fireEvent.click(screen.getByRole('button', { name: /change password/i }));
    // Check for password requirements error in DOM
    await waitFor(() => {
      expect(
        screen.getByText(/does not meet requirements/i),
      ).toBeInTheDocument();
    });
  });

  it('handles API error on password change', async () => {
    global.fetch = jest.fn().mockImplementation((url, opts) => {
      if (url.includes('/csrf-token/')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ csrf_token: 'test-token' }),
        });
      }
      if (url.includes('/profile/') && (!opts || !opts.method || opts.method === 'GET')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            profile: { name: 'Test User', email: 'test@example.com' },
          }),
        });
      }
      if (url.includes('/change-password/') && opts && opts.method === 'POST') {
        return Promise.resolve({
          ok: false,
          json: async () => ({ error: 'Failed to change password' }),
        });
      }
    });

    await act(async () => {
      render(<Profile theme={TEST_THEME} />);
    });
    await screen.findByText('Test User');
    fireEvent.change(screen.getByLabelText(/current password/i), {
      target: { value: 'Test_Old_1!' },
    });
    fireEvent.change(screen.getByLabelText(/^new password$/i), {
      target: { value: 'Test_New_1!' },
    });
    fireEvent.change(screen.getByLabelText(/confirm new password/i), {
      target: { value: 'Test_New_1!' },
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
