import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Profile from './Profile';

const FAKE_TOKEN = 'fake-access-token';
const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

describe('Profile component', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
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
    render(<Profile accessToken={FAKE_TOKEN} />);
    expect(screen.getByText(/loading profile/i)).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith(
      `${API_BASE}/api/profile/`,
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: `Bearer ${FAKE_TOKEN}`,
        }),
      }),
    );
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
    render(<Profile accessToken={FAKE_TOKEN} />);
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
    expect(
      await screen.findByText(/profile updated successfully/i),
    ).toBeInTheDocument();
    expect(screen.getByText('New Name')).toBeInTheDocument();
    expect(screen.getByText('new@example.com')).toBeInTheDocument();
  });

  it('shows validation error for invalid email', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        profile: { name: 'Test User', email: 'test@example.com' },
      }),
    });
    render(<Profile accessToken={FAKE_TOKEN} />);
    await screen.findByText('Test User');
    fireEvent.click(screen.getByText(/edit profile/i));
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'invalid-email' },
    });
    fireEvent.click(screen.getByText(/^save$/i));
    expect(
      await screen.findByText(/invalid email format/i),
    ).toBeInTheDocument();
  });

  it('handles API error on profile fetch', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ error: 'Failed to fetch profile' }),
    });
    render(<Profile accessToken={FAKE_TOKEN} />);
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
    render(<Profile accessToken={FAKE_TOKEN} />);
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
    expect(
      await screen.findByText(/password changed successfully/i),
    ).toBeInTheDocument();
  });

  it('shows error if new passwords do not match', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        profile: { name: 'Test User', email: 'test@example.com' },
      }),
    });
    render(<Profile accessToken={FAKE_TOKEN} />);
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
    expect(
      await screen.findByText(/new passwords do not match/i),
    ).toBeInTheDocument();
  });

  it('shows error if password does not meet requirements', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        profile: { name: 'Test User', email: 'test@example.com' },
      }),
    });
    render(<Profile accessToken={FAKE_TOKEN} />);
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
    expect(
      await screen.findByText(/does not meet requirements/i),
    ).toBeInTheDocument();
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
    render(<Profile accessToken={FAKE_TOKEN} />);
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
    expect(
      await screen.findByText(/failed to change password/i),
    ).toBeInTheDocument();
  });
});
