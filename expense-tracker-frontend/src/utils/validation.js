/**
 * Email validation
 */
export function validateEmail(email) {
  return /.+@.+\..+/.test(email);
}

/**
 * Password validation rules
 * Each rule has a test function and a message
 */
export const passwordRules = [
  {
    test: (pw) => pw.length >= 8,
    message: 'At least 8 characters',
  },
  {
    test: (pw) => /[A-Z]/.test(pw),
    message: 'At least one uppercase letter',
  },
  {
    test: (pw) => /[a-z]/.test(pw),
    message: 'At least one lowercase letter',
  },
  {
    test: (pw) => /[0-9]/.test(pw),
    message: 'At least one number',
  },
  {
    test: (pw) => /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(pw),
    message: 'At least one special character (!@#$%^&* etc.)',
  },
];

/**
 * Validate password against all rules
 * Returns array of rule results
 */
export function validatePasswordRules(password) {
  return passwordRules.map((rule) => ({
    test: rule.test(password),
    message: rule.message,
  }));
}

/**
 * Check if all password rules pass
 */
export function isPasswordValid(password) {
  return passwordRules.every((rule) => rule.test(password));
}
