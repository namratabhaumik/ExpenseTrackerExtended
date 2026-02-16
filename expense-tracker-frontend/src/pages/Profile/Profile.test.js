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

    expect(await screen.findByText('Test User')).toBeInTheDocument();
    expect(screen.getByText('test@example.com')).toBeInTheDocument();
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

  it('shows error if new passwords do not match', async () => {
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
      target: { value: 'Test_New_1!' },
    });
    fireEvent.change(screen.getByLabelText(/confirm new password/i), {
      target: { value: 'DifferentPass!' },
    });
    fireEvent.click(screen.getByRole('button', { name: /change password/i }));

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

    await waitFor(() => {
      expect(mockToastError).toHaveBeenCalledWith(
        expect.stringMatching(/failed to change password/i),
        expect.anything(),
      );
    });
  });
});
