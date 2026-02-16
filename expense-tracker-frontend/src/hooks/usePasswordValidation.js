import { useState, useCallback } from 'react';
import { validatePasswordRules, isPasswordValid } from '../utils/validation';

/**
 * Custom hook for password validation
 * Returns validation state for each password rule and overall validity
 */
export function usePasswordValidation(initialPassword = '') {
  const [password, setPassword] = useState(initialPassword);
  const [validationRules, setValidationRules] = useState([]);

  const updatePassword = useCallback((newPassword) => {
    setPassword(newPassword);
    const rules = validatePasswordRules(newPassword);
    setValidationRules(rules);
  }, []);

  const isValid = isPasswordValid(password);

  return {
    password,
    setPassword: updatePassword,
    validationRules,
    isValid,
  };
}
