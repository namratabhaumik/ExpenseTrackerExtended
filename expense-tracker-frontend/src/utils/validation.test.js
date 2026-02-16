import { validateEmail, validatePasswordRules, isPasswordValid } from './validation';

describe('validation utils', () => {
  test('validateEmail', () => {
    expect(validateEmail('foo@example.com')).toBe(true);
    expect(validateEmail('invalid-email')).toBe(false);
    expect(validateEmail('a@b.c')).toBe(true);
  });

  test('validatePasswordRules and isPasswordValid', () => {
    const weak = 'short';
    const medium = 'Abcdef12';
    const strong = 'Abcdef1!';

    const weakRules = validatePasswordRules(weak);
    expect(weakRules.some((r) => r.test === false)).toBe(true);
    expect(isPasswordValid(weak)).toBe(false);

    const mediumRules = validatePasswordRules(medium);
    expect(mediumRules.some((r) => r.test === false)).toBe(true);
    expect(isPasswordValid(medium)).toBe(false);

    const strongRules = validatePasswordRules(strong);
    expect(strongRules.every((r) => r.test === true)).toBe(true);
    expect(isPasswordValid(strong)).toBe(true);
  });
});
