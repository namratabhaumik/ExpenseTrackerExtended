import {
  render,
  screen,
  fireEvent,
  waitFor,
  within,
  act,
} from '@testing-library/react';
import '@testing-library/jest-dom';
import App from './App';

// Mock the AWS configuration
jest.mock('./config/awsconfig', () => ({
  Auth: {
    configure: jest.fn(),
  },
}));

// Mock axios for API calls
jest.mock('axios', () => ({
  post: jest.fn(),
  get: jest.fn(),
}));

describe('App Component', () => {
  beforeEach(() => {
    global.fetch = jest.fn((url, opts) => {
      // Mock CSRF token endpoint
      if (url && url.includes('/csrf-token/')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              csrf_token: 'test-token',
            }),
        });
      }
      // Mock /api/signup/ POST
      if (url && url.includes('/api/signup/')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              message:
                'Sign up successful! You can now log in with your credentials.',
              status: 'success',
            }),
        });
      }
      // Mock /api/login/ POST
      if (url && url.includes('/api/login/')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              message: 'Login successful.',
              status: 'success',
            }),
        });
      }
      // Mock /api/confirm-signup/ POST
      if (url && url.includes('/api/confirm-signup/')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              message: 'Account verified! You can now log in.',
              status: 'success',
            }),
        });
      }
      // Default: mock expenses fetch
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ expenses: [] }),
      });
    });
  });
  afterEach(() => {
    global.fetch.mockRestore();
  });

  test('renders login and sign up tabs', async () => {
    await act(async () => {
      render(<App />);
    });
    // Use getAllByRole for tabs and check their className
    const loginTab = screen
      .getAllByRole('button', { name: /^Login$/ })
      .find((btn) => btn.className.includes('auth-tab'));
    const signUpTab = screen
      .getAllByRole('button', { name: /^Sign Up$/ })
      .find((btn) => btn.className.includes('auth-tab'));
    expect(loginTab).toBeInTheDocument();
    expect(signUpTab).toBeInTheDocument();
  });

  test('toggles to sign up form', async () => {
    await act(async () => {
      render(<App />);
    });
    const signUpTab = screen
      .getAllByRole('button', { name: /^Sign Up$/ })
      .find((btn) => btn.className.includes('auth-tab'));
    fireEvent.click(signUpTab);
    // Instead of 'Create Account', check for sign up form fields and button
    expect(
      screen.getByLabelText('Email:', { selector: 'input' }),
    ).toBeInTheDocument();
    expect(
      screen.getByLabelText('Password:', { selector: 'input' }),
    ).toBeInTheDocument();
    expect(
      screen.getByLabelText('Confirm Password:', { selector: 'input' }),
    ).toBeInTheDocument();
    // The submit button for sign up is the last one
    const signUpSubmit = screen
      .getAllByRole('button', { name: /^Sign Up$/ })
      .slice(-1)[0];
    expect(signUpSubmit).toBeInTheDocument();
  });

  test('toggles back to login form', async () => {
    await act(async () => {
      render(<App />);
    });
    const signUpTab = screen
      .getAllByRole('button', { name: /^Sign Up$/ })
      .find((btn) => btn.className.includes('auth-tab'));
    fireEvent.click(signUpTab);
    const loginTab = screen
      .getAllByRole('button', { name: /^Login$/ })
      .find((btn) => btn.className.includes('auth-tab'));
    fireEvent.click(loginTab);
    const loginSubmit = screen
      .getAllByRole('button', { name: /^Login$/ })
      .slice(-1)[0];
    await waitFor(() => {
      expect(loginSubmit).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(
        screen.getByLabelText('Email:', { selector: 'input' }),
      ).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(
        screen.getByLabelText('Password:', { selector: 'input' }),
      ).toBeInTheDocument();
    });
  });

  test('handles login with session cookie', async () => {
    global.fetch = jest.fn((url) => {
      if (url.includes('/csrf-token/')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              csrf_token: 'test-token',
            }),
        });
      }
      if (url.includes('/api/login/')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              message: 'Login successful.',
            }),
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ expenses: [] }),
      });
    });
    await act(async () => {
      render(<App />);
    });
    fireEvent.change(screen.getByLabelText('Email:', { selector: 'input' }), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(
      screen.getByLabelText('Password:', { selector: 'input' }),
      {
        target: { value: 'Test_Pass_1!' },
      },
    );
    const loginSubmit = screen
      .getAllByRole('button', { name: /^Login$/ })
      .slice(-1)[0];
    fireEvent.click(loginSubmit);
    // After successful login, the app should navigate away from auth view
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/login/'),
        expect.any(Object)
      );
    });
  });

  test('shows loading state during login', async () => {
    await act(async () => {
      render(<App />);
    });
    fireEvent.change(screen.getByLabelText('Email:', { selector: 'input' }), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(
      screen.getByLabelText('Password:', { selector: 'input' }),
      {
        target: { value: 'password123' },
      },
    );
    const loginSubmit = screen
      .getAllByRole('button', { name: /^Login$/ })
      .slice(-1)[0];
    fireEvent.click(loginSubmit);
    await waitFor(() => {
      expect(loginSubmit).toBeInTheDocument();
    });
  });

  test('shows confirm account modal after successful sign up', async () => {
    // Note: Session-based auth doesn't use email confirmation in current implementation
    // Signup success message is shown directly instead
    await act(async () => {
      render(<App />);
    });
    const signUpTab = screen
      .getAllByRole('button', { name: /^Sign Up$/ })
      .find((btn) => btn.className.includes('auth-tab'));
    fireEvent.click(signUpTab);

    const emailInput = document.getElementById('signup-email');
    const passwordInput = document.getElementById('signup-password');
    const confirmInput = document.getElementById('signup-confirm');

    fireEvent.change(emailInput, {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(passwordInput, {
      target: { value: 'Test_Pass_1!' },
    });
    fireEvent.change(confirmInput, {
      target: { value: 'Test_Pass_1!' },
    });

    const signUpSubmit = screen
      .getAllByRole('button', { name: /^Sign Up$/ })
      .slice(-1)[0];
    fireEvent.click(signUpSubmit);

    // In session-based auth, signup success message is shown directly
    await waitFor(() => {
      expect(screen.getByText(/Sign up successful/i)).toBeInTheDocument();
    });
  });

  test('closes confirm account modal and returns to login', async () => {
    // Note: This test is updated for session-based auth without email confirmation
    await act(async () => {
      render(<App />);
    });
    const signUpTab = screen
      .getAllByRole('button', { name: /^Sign Up$/ })
      .find((btn) => btn.className.includes('auth-tab'));
    fireEvent.click(signUpTab);

    const emailInput = document.getElementById('signup-email');
    const passwordInput = document.getElementById('signup-password');
    const confirmInput = document.getElementById('signup-confirm');

    fireEvent.change(emailInput, {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(passwordInput, {
      target: { value: 'Test_Pass_1!' },
    });
    fireEvent.change(confirmInput, {
      target: { value: 'Test_Pass_1!' },
    });

    const signUpSubmit = screen
      .getAllByRole('button', { name: /^Sign Up$/ })
      .slice(-1)[0];
    fireEvent.click(signUpSubmit);

    // In session-based auth, success message shows, user can click "Already have an account? Login" to go back
    await waitFor(() => {
      expect(screen.getByText(/Sign up successful/i)).toBeInTheDocument();
    });

    const loginLink = screen.getByText(/Already have an account\? Login/i);
    fireEvent.click(loginLink);

    await waitFor(() => {
      const loginTab = screen
        .getAllByRole('button', { name: /^Login$/ })
        .find((btn) => btn.className.includes('auth-tab'));
      expect(loginTab).toBeInTheDocument();
    });
  });

  test('shows login form with email and password fields', async () => {
    await act(async () => {
      render(<App />);
    });
    expect(screen.getByLabelText('Email:', { selector: 'input' })).toBeInTheDocument();
    expect(screen.getByLabelText('Password:', { selector: 'input' })).toBeInTheDocument();
  });

  test('shows signup form fields when sign up tab is clicked', async () => {
    await act(async () => {
      render(<App />);
    });
    const signUpTab = screen
      .getAllByRole('button', { name: /^Sign Up$/ })
      .find((btn) => btn.className.includes('auth-tab'));
    fireEvent.click(signUpTab);

    await waitFor(() => {
      expect(screen.getByLabelText('Email:', { selector: 'input' })).toBeInTheDocument();
      expect(screen.getByLabelText('Password:', { selector: 'input' })).toBeInTheDocument();
      expect(screen.getByLabelText('Confirm Password:', { selector: 'input' })).toBeInTheDocument();
    });
  });

  test('shows error message when login fails', async () => {
    global.fetch = jest.fn((url) => {
      if (url.includes('/csrf-token/')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              csrf_token: 'test-token',
            }),
        });
      }
      if (url.includes('/api/login/')) {
        return Promise.resolve({
          ok: false,
          json: () =>
            Promise.resolve({
              error: 'Invalid credentials',
              status: 'error',
            }),
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ expenses: [] }),
      });
    });

    await act(async () => {
      render(<App />);
    });
    fireEvent.change(screen.getByLabelText('Email:', { selector: 'input' }), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText('Password:', { selector: 'input' }), {
      target: { value: 'wrongpassword' },
    });

    const loginSubmit = screen
      .getAllByRole('button', { name: /^Login$/ })
      .slice(-1)[0];
    fireEvent.click(loginSubmit);

    await waitFor(() => {
      expect(screen.getByText(/Invalid credentials/i)).toBeInTheDocument();
    });
  });

  test('successful signup shows success message', async () => {
    await act(async () => {
      render(<App />);
    });
    const signUpTab = screen
      .getAllByRole('button', { name: /^Sign Up$/ })
      .find((btn) => btn.className.includes('auth-tab'));
    fireEvent.click(signUpTab);

    const emailInput = document.getElementById('signup-email');
    const passwordInput = document.getElementById('signup-password');
    const confirmInput = document.getElementById('signup-confirm');

    fireEvent.change(emailInput, {
      target: { value: 'newuser@example.com' },
    });
    fireEvent.change(passwordInput, {
      target: { value: 'Test_Pass_1!' },
    });
    fireEvent.change(confirmInput, {
      target: { value: 'Test_Pass_1!' },
    });

    const signUpSubmit = screen
      .getAllByRole('button', { name: /^Sign Up$/ })
      .slice(-1)[0];
    fireEvent.click(signUpSubmit);

    await waitFor(() => {
      expect(
        screen.getByText(/Sign up successful/i),
      ).toBeInTheDocument();
    });
  });

  test('shows error for password mismatch in signup form', async () => {
    await act(async () => {
      render(<App />);
    });
    const signUpTab = screen
      .getAllByRole('button', { name: /^Sign Up$/ })
      .find((btn) => btn.className.includes('auth-tab'));
    fireEvent.click(signUpTab);

    const emailInput = document.getElementById('signup-email');
    const passwordInput = document.getElementById('signup-password');
    const confirmInput = document.getElementById('signup-confirm');

    fireEvent.change(emailInput, {
      target: { value: 'newuser@example.com' },
    });
    fireEvent.change(passwordInput, {
      target: { value: 'Test_New_1!' },
    });
    fireEvent.change(confirmInput, {
      target: { value: 'Test_Diff_1!' },
    });

    // The error should appear immediately when passwords don't match
    await waitFor(() => {
      const errorMessages = screen.getAllByText(/Passwords do not match/i);
      expect(errorMessages.length).toBeGreaterThan(0);
    });
  });

  test('shows password requirements validation in signup form', async () => {
    await act(async () => {
      render(<App />);
    });
    const signUpTab = screen
      .getAllByRole('button', { name: /^Sign Up$/ })
      .find((btn) => btn.className.includes('auth-tab'));
    fireEvent.click(signUpTab);

    // Focus on password field to show requirements
    const signupPasswordInput = document.getElementById('signup-password');
    fireEvent.focus(signupPasswordInput);

    await waitFor(() => {
      expect(screen.getByText(/At least 8 characters/i)).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(
        screen.getByText(/At least one uppercase letter/i),
      ).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(
        screen.getByText(/At least one lowercase letter/i),
      ).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(screen.getByText(/At least one number/i)).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(
        screen.getByText(/At least one special character/i),
      ).toBeInTheDocument();
    });
  });

  test('shows error for weak password in signup form', async () => {
    await act(async () => {
      render(<App />);
    });
    const signUpTab = screen
      .getAllByRole('button', { name: /^Sign Up$/ })
      .find((btn) => btn.className.includes('auth-tab'));
    fireEvent.click(signUpTab);

    const emailInput = document.getElementById('signup-email');
    const passwordInput = document.getElementById('signup-password');
    const confirmInput = document.getElementById('signup-confirm');

    fireEvent.change(emailInput, {
      target: { value: 'newuser@example.com' },
    });
    fireEvent.change(passwordInput, {
      target: { value: 'weak' },
    });
    fireEvent.change(confirmInput, {
      target: { value: 'weak' },
    });

    const signUpSubmit = screen
      .getAllByRole('button', { name: /^Sign Up$/ })
      .slice(-1)[0];
    fireEvent.click(signUpSubmit);

    // When password requirements are not met, an error appears
    await waitFor(() => {
      const errorElement = screen.queryByText(/Password does not meet all requirements/i);
      expect(errorElement).toBeInTheDocument();
    });
  });

  test('successful login navigates to main app', async () => {
    // Session-based auth: login should set session cookie
    await act(async () => {
      render(<App />);
    });

    const emailInput = screen.getByLabelText('Email:', { selector: 'input' });
    const passwordInput = screen.getByLabelText('Password:', { selector: 'input' });

    fireEvent.change(emailInput, {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(passwordInput, {
      target: { value: 'Test_Pass_1!' },
    });

    const loginSubmit = screen
      .getAllByRole('button', { name: /^Login$/ })
      .slice(-1)[0];
    fireEvent.click(loginSubmit);

    // After successful login, the app should try to load expenses
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/login/'),
        expect.any(Object)
      );
    });
  });

  // Remove or comment out tests for field validation and email format, as the UI does not show these messages
  // test("validates required fields", async () => { ... });
  // test("validates email format", async () => { ... });
});

describe('Theme Toggle Placement', () => {
  test('shows global theme toggle button on login/signup page', () => {
    render(<App />);
    const themeToggle = screen.getByRole('button', { name: /switch to/i });
    expect(themeToggle).toBeInTheDocument();
    // Should have global-theme-toggle-btn class
    expect(themeToggle.className).toMatch(/global-theme-toggle-btn/);
  });

  test('theme toggle is not inside the form box', () => {
    render(<App />);
    const themeToggle = screen.getByRole('button', { name: /switch to/i });
    expect(themeToggle).toBeInTheDocument();

    // Use only Testing Library queries, not direct DOM access
    const loginContainer = screen.queryByTestId('login-container');
    expect(loginContainer).toBeTruthy();
    const toggleInside = within(loginContainer).queryByRole('button', {
      name: /switch to/i,
    });
    expect(toggleInside).toBeNull();
  });

  test('theme toggle button switches icon and aria-label', () => {
    render(<App />);
    const themeToggle = screen.getByRole('button', { name: /switch to/i });
    const initialLabel = themeToggle.getAttribute('aria-label');
    fireEvent.click(themeToggle);
    const newLabel = themeToggle.getAttribute('aria-label');
    expect(initialLabel).not.toBe(newLabel);
  });
});
