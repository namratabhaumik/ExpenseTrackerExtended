import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AuthForm from './Login';
import * as apiService from '../../services/api';

// Mock the API service and components
jest.mock('../../services/api');
jest.mock('./components/ConfirmAccountModal', () => {
  return function MockConfirmAccountModal() {
    return <div data-testid="confirm-account-modal">Modal</div>;
  };
});

describe('AuthForm (Login Component) - Session-Based Auth Tests', () => {
  const mockOnLoginSuccess = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    // Mock the apiPost to resolve successfully by default
    apiService.apiPost.mockResolvedValue({});
    apiService.clearCSRFTokenCache.mockImplementation(() => {});
  });

  describe('Session-Based Auth - CSRF Token Management', () => {
    test('clears CSRF token cache after successful login', async () => {
      apiService.apiPost.mockResolvedValue({ success: true });

      render(<AuthForm onLoginSuccess={mockOnLoginSuccess} theme="light" />);

      fireEvent.change(screen.getByLabelText('Email'), {
        target: { value: 'test@example.com' },
      });
      fireEvent.change(screen.getByLabelText('Password'), {
        target: { value: 'Test_Pass_1!' },
      });
      fireEvent.click(screen.getAllByRole('button', { name: 'Login' })[1]);

      await waitFor(() => {
        expect(apiService.clearCSRFTokenCache).toHaveBeenCalledTimes(1);
      });
    });

    test('does not clear CSRF token cache on login error', async () => {
      const apiError = new apiService.APIError('Login failed', 401, {});
      apiService.apiPost.mockRejectedValue(apiError);

      render(<AuthForm onLoginSuccess={mockOnLoginSuccess} theme="light" />);

      fireEvent.change(screen.getByLabelText('Email'), {
        target: { value: 'test@example.com' },
      });
      fireEvent.change(screen.getByLabelText('Password'), {
        target: { value: 'Test_Pass_1!' },
      });
      fireEvent.click(screen.getAllByRole('button', { name: 'Login' })[1]);

      await waitFor(() => {
        expect(apiService.clearCSRFTokenCache).not.toHaveBeenCalled();
      });
    });

    test('sends login credentials via apiPost to /api/login/ endpoint', async () => {
      apiService.apiPost.mockResolvedValue({ sessionId: 'test-session-id' });

      render(<AuthForm onLoginSuccess={mockOnLoginSuccess} theme="light" />);

      const emailInputs = screen.getAllByLabelText('Email');
      const passwordInputs = screen.getAllByLabelText('Password');
      fireEvent.change(emailInputs[0], { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInputs[0], { target: { value: 'Test_Pass_1!' } });
      fireEvent.click(screen.getAllByRole('button', { name: 'Login' })[1]);

      await waitFor(() => {
        expect(apiService.apiPost).toHaveBeenCalledWith('/api/login/', {
          email: 'test@example.com',
          password: 'Test_Pass_1!',
        });
      });
    });

    test('sends signup credentials via apiPost to /api/signup/ endpoint', async () => {
      apiService.apiPost.mockResolvedValue({ success: true });

      render(<AuthForm onLoginSuccess={mockOnLoginSuccess} theme="light" />);

      fireEvent.click(screen.getAllByRole('button', { name: 'Sign Up' })[0]);

      const emailInputs = screen.getAllByLabelText('Email');
      const passwordInputs = screen.getAllByLabelText('Password');
      fireEvent.change(emailInputs[0], { target: { value: 'newuser@example.com' } });
      fireEvent.change(passwordInputs[0], { target: { value: 'Test_Pass_1!' } });
      fireEvent.change(screen.getByLabelText('Confirm Password'), { target: { value: 'Test_Pass_1!' } });
      fireEvent.click(screen.getAllByRole('button', { name: 'Sign Up' })[1]);

      await waitFor(() => {
        expect(apiService.apiPost).toHaveBeenCalledWith('/api/signup/', {
          email: 'newuser@example.com',
          password: 'Test_Pass_1!',
        });
      });
    });
  });

  describe('Login Flow - Callbacks and Error Handling', () => {
    test('calls onLoginSuccess callback after successful login', async () => {
      apiService.apiPost.mockResolvedValue({ success: true });

      render(<AuthForm onLoginSuccess={mockOnLoginSuccess} theme="light" />);

      fireEvent.change(screen.getByLabelText('Email'), {
        target: { value: 'test@example.com' },
      });
      fireEvent.change(screen.getByLabelText('Password'), {
        target: { value: 'Test_Pass_1!' },
      });
      fireEvent.click(screen.getAllByRole('button', { name: 'Login' })[1]);

      await waitFor(() => {
        expect(mockOnLoginSuccess).toHaveBeenCalledTimes(1);
      });
    });

    test('does not call onLoginSuccess on login error', async () => {
      const apiError = new apiService.APIError('Login failed', 401, {});
      apiService.apiPost.mockRejectedValue(apiError);

      render(<AuthForm onLoginSuccess={mockOnLoginSuccess} theme="light" />);

      fireEvent.change(screen.getByLabelText('Email'), {
        target: { value: 'test@example.com' },
      });
      fireEvent.change(screen.getByLabelText('Password'), {
        target: { value: 'Test_Pass_1!' },
      });
      fireEvent.click(screen.getAllByRole('button', { name: 'Login' })[1]);

      await waitFor(() => {
        expect(mockOnLoginSuccess).not.toHaveBeenCalled();
      });
    });

    test('displays error message on login failure', async () => {
      apiService.apiPost.mockRejectedValueOnce(
        new apiService.APIError('Invalid email or password', 401, {})
      );

      render(<AuthForm onLoginSuccess={mockOnLoginSuccess} theme="light" />);

      fireEvent.change(screen.getAllByLabelText('Email')[0], {
        target: { value: 'wrong@example.com' },
      });
      fireEvent.change(screen.getAllByLabelText('Password')[0], {
        target: { value: 'WrongPass1!' },
      });
      fireEvent.click(screen.getAllByRole('button', { name: 'Login' })[1]);

      await waitFor(() => {
        expect(screen.queryByText(/Invalid email or password|Login failed/)).toBeInTheDocument();
      });
    });
  });

  describe('Signup Flow - Callbacks and Error Handling', () => {
    test('does not call onLoginSuccess on signup error', async () => {
      const apiError = new apiService.APIError('Signup failed', 400, {});
      apiService.apiPost.mockRejectedValue(apiError);

      render(<AuthForm onLoginSuccess={mockOnLoginSuccess} theme="light" />);

      fireEvent.click(screen.getAllByRole('button', { name: 'Sign Up' })[0]);

      fireEvent.change(screen.getByLabelText('Email'), {
        target: { value: 'test@example.com' },
      });
      fireEvent.change(screen.getAllByLabelText('Password')[0], {
        target: { value: 'Test_Pass_1!' },
      });
      fireEvent.change(screen.getByLabelText('Confirm Password'), {
        target: { value: 'Test_Pass_1!' },
      });
      fireEvent.click(screen.getAllByRole('button', { name: 'Sign Up' })[1]);

      await waitFor(() => {
        expect(mockOnLoginSuccess).not.toHaveBeenCalled();
      });
    });

    test('displays success message after signup', async () => {
      apiService.apiPost.mockResolvedValue({ success: true });

      render(<AuthForm onLoginSuccess={mockOnLoginSuccess} theme="light" />);

      fireEvent.click(screen.getAllByRole('button', { name: 'Sign Up' })[0]);

      fireEvent.change(screen.getByLabelText('Email'), {
        target: { value: 'newuser@example.com' },
      });
      fireEvent.change(screen.getAllByLabelText('Password')[0], {
        target: { value: 'Test_Pass_1!' },
      });
      fireEvent.change(screen.getByLabelText('Confirm Password'), {
        target: { value: 'Test_Pass_1!' },
      });
      fireEvent.click(screen.getAllByRole('button', { name: 'Sign Up' })[1]);

      await waitFor(() => {
        expect(screen.getByText('Sign up successful! You can now log in with your credentials.')).toBeInTheDocument();
      });
    });

    test('displays error message on signup failure', async () => {
      apiService.apiPost.mockRejectedValueOnce(
        new apiService.APIError('User with this email already exists', 400, {})
      );

      render(<AuthForm onLoginSuccess={mockOnLoginSuccess} theme="light" />);

      fireEvent.click(screen.getAllByRole('button', { name: 'Sign Up' })[0]);

      fireEvent.change(screen.getByLabelText('Email'), {
        target: { value: 'existing@example.com' },
      });
      fireEvent.change(screen.getAllByLabelText('Password')[0], {
        target: { value: 'Test_Pass_1!' },
      });
      fireEvent.change(screen.getByLabelText('Confirm Password'), {
        target: { value: 'Test_Pass_1!' },
      });

      const signupButton = screen.getAllByRole('button', { name: 'Sign Up' })[1];
      fireEvent.click(signupButton);

      await waitFor(() => {
        expect(screen.queryByText(/User with this email already exists|Sign up failed/)).toBeInTheDocument();
      });
    });
  });

  describe('Form Rendering and Tab Navigation', () => {
    test('renders login form with email and password fields', () => {
      render(<AuthForm onLoginSuccess={mockOnLoginSuccess} theme="light" />);

      expect(screen.getByLabelText('Email')).toBeInTheDocument();
      expect(screen.getByLabelText('Password')).toBeInTheDocument();
      expect(screen.getAllByRole('button', { name: 'Login' })[1]).toBeInTheDocument();
    });

    test('renders signup form with confirm password field', () => {
      render(<AuthForm onLoginSuccess={mockOnLoginSuccess} theme="light" />);

      fireEvent.click(screen.getAllByRole('button', { name: 'Sign Up' })[0]);

      expect(screen.getByLabelText('Email')).toBeInTheDocument();
      expect(screen.getAllByLabelText('Password')[0]).toBeInTheDocument();
      expect(screen.getByLabelText('Confirm Password')).toBeInTheDocument();
    });

    test('switches between login and signup tabs', () => {
      render(<AuthForm onLoginSuccess={mockOnLoginSuccess} theme="light" />);

      const signupTab = screen.getAllByRole('button', { name: 'Sign Up' })[0];
      fireEvent.click(signupTab);
      expect(signupTab).toHaveAttribute('aria-selected', 'true');

      const loginTab = screen.getAllByRole('button', { name: 'Login' })[0];
      fireEvent.click(loginTab);
      expect(loginTab).toHaveAttribute('aria-selected', 'true');
      expect(signupTab).toHaveAttribute('aria-selected', 'false');
    });

    test('switches to signup tab when clicking signup link in login form', () => {
      render(<AuthForm onLoginSuccess={mockOnLoginSuccess} theme="light" />);

      const signupLink = screen.getByText("Don't have an account? Sign Up");
      fireEvent.click(signupLink);

      expect(screen.getByLabelText('Confirm Password')).toBeInTheDocument();
    });

    test('switches to login tab when clicking login link in signup form', () => {
      render(<AuthForm onLoginSuccess={mockOnLoginSuccess} theme="light" />);

      fireEvent.click(screen.getAllByRole('button', { name: 'Sign Up' })[0]);

      const loginLink = screen.getByText('Already have an account? Login');
      fireEvent.click(loginLink);

      expect(screen.queryByLabelText('Confirm Password')).not.toBeInTheDocument();
    });
  });

  describe('Form Field Behavior', () => {
    test('updates email input on change in login form', () => {
      render(<AuthForm onLoginSuccess={mockOnLoginSuccess} theme="light" />);

      const emailInput = screen.getAllByLabelText('Email')[0];
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });

      expect(emailInput).toHaveValue('test@example.com');
    });

    test('toggles password visibility in login form', () => {
      render(<AuthForm onLoginSuccess={mockOnLoginSuccess} theme="light" />);

      const passwordInput = screen.getByLabelText('Password');
      expect(passwordInput).toHaveAttribute('type', 'password');

      const showPasswordButton = screen.getByLabelText('Show password');
      fireEvent.click(showPasswordButton);

      expect(passwordInput).toHaveAttribute('type', 'text');
    });

    test('validates email format in signup form', async () => {
      render(<AuthForm onLoginSuccess={mockOnLoginSuccess} theme="light" />);

      fireEvent.click(screen.getAllByRole('button', { name: 'Sign Up' })[0]);

      const emailInput = screen.getByLabelText('Email');
      fireEvent.change(emailInput, { target: { value: 'invalid-email' } });

      await waitFor(() => {
        expect(screen.getByText('Invalid email format.')).toBeInTheDocument();
      });
    });

    test('validates password match in signup form', () => {
      render(<AuthForm onLoginSuccess={mockOnLoginSuccess} theme="light" />);

      fireEvent.click(screen.getAllByRole('button', { name: 'Sign Up' })[0]);

      fireEvent.change(screen.getByLabelText('Email'), {
        target: { value: 'test@example.com' },
      });
      fireEvent.change(screen.getAllByLabelText('Password')[0], {
        target: { value: 'Test_Pass_1!' },
      });
      fireEvent.change(screen.getByLabelText('Confirm Password'), {
        target: { value: 'Different_Pass_1!' },
      });

      expect(screen.getByText('Passwords do not match.')).toBeInTheDocument();
    });

    test('validates password requirements in signup form', async () => {
      render(<AuthForm onLoginSuccess={mockOnLoginSuccess} theme="light" />);

      fireEvent.click(screen.getAllByRole('button', { name: 'Sign Up' })[0]);

      fireEvent.change(screen.getByLabelText('Email'), {
        target: { value: 'test@example.com' },
      });
      fireEvent.change(screen.getAllByLabelText('Password')[0], {
        target: { value: 'weak' },
      });
      fireEvent.change(screen.getByLabelText('Confirm Password'), {
        target: { value: 'weak' },
      });

      const signupButton = screen.getAllByRole('button', { name: 'Sign Up' })[1];
      fireEvent.click(signupButton);

      await waitFor(() => {
        expect(screen.getByText('Password does not meet all requirements.')).toBeInTheDocument();
      });

      expect(apiService.apiPost).not.toHaveBeenCalled();
    });

    test('displays password requirements when password field is focused', async () => {
      render(<AuthForm onLoginSuccess={mockOnLoginSuccess} theme="light" />);

      fireEvent.click(screen.getAllByRole('button', { name: 'Sign Up' })[0]);

      const passwordInput = screen.getAllByLabelText('Password')[0];
      fireEvent.focus(passwordInput);

      await waitFor(() => {
        expect(screen.getByText('At least 8 characters')).toBeInTheDocument();
        expect(screen.getByText('At least one uppercase letter')).toBeInTheDocument();
        expect(screen.getByText('At least one lowercase letter')).toBeInTheDocument();
        expect(screen.getByText('At least one number')).toBeInTheDocument();
        expect(screen.getByText('At least one special character')).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility and Theme', () => {
    test('has required attributes on form inputs', () => {
      render(<AuthForm onLoginSuccess={mockOnLoginSuccess} theme="light" />);

      expect(screen.getByLabelText('Email')).toHaveAttribute('required');
      expect(screen.getByLabelText('Password')).toHaveAttribute('required');
    });

    test('has required attributes on signup inputs', () => {
      render(<AuthForm onLoginSuccess={mockOnLoginSuccess} theme="light" />);

      fireEvent.click(screen.getAllByRole('button', { name: 'Sign Up' })[0]);

      expect(screen.getByLabelText('Email')).toHaveAttribute('required');
      expect(screen.getByLabelText('Confirm Password')).toHaveAttribute('required');
    });

    test('password eye icon has proper aria labels', () => {
      render(<AuthForm onLoginSuccess={mockOnLoginSuccess} theme="light" />);

      expect(screen.getByLabelText('Show password')).toBeInTheDocument();

      const eyeButton = screen.getByLabelText('Show password');
      fireEvent.click(eyeButton);

      expect(screen.getByLabelText('Hide password')).toBeInTheDocument();
    });

    test('tab buttons have proper aria-selected attributes', () => {
      render(<AuthForm onLoginSuccess={mockOnLoginSuccess} theme="light" />);

      const loginTab = screen.getAllByRole('button', { name: 'Login' })[0];
      const signupTab = screen.getAllByRole('button', { name: 'Sign Up' })[0];

      expect(loginTab).toHaveAttribute('aria-selected', 'true');
      expect(signupTab).toHaveAttribute('aria-selected', 'false');
    });

    test('applies theme class to login container', () => {
      render(<AuthForm onLoginSuccess={mockOnLoginSuccess} theme="dark" />);

      const loginContainer = screen.getByTestId('login-container');
      expect(loginContainer).toHaveClass('dark');
    });
  });

  describe('Component Integration', () => {
    test('renders confirm account modal', () => {
      render(<AuthForm onLoginSuccess={mockOnLoginSuccess} theme="light" />);

      expect(screen.getByTestId('confirm-account-modal')).toBeInTheDocument();
    });
  });
});
