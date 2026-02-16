import { render, screen, fireEvent } from '@testing-library/react';
import { usePasswordValidation } from './usePasswordValidation';

function HookTester() {
  const { password, setPassword, validationRules, isValid } = usePasswordValidation('');
  return (
    <div>
      <div data-testid="password">{password}</div>
      <div data-testid="isValid">{String(isValid)}</div>
      <ul>
        {validationRules.map((r, i) => (
          <li key={i} data-testid={`rule-${i}`}>
            {String(r.test)}
          </li>
        ))}
      </ul>
      <button onClick={() => setPassword('Test_Pass_1!')}>set-strong</button>
    </div>
  );
}

describe('usePasswordValidation', () => {
  test('initial state and update', () => {
    render(<HookTester />);

    expect(screen.getByTestId('password').textContent).toBe('');
    expect(screen.getByTestId('isValid').textContent).toBe('false');

    // update to a strong password
    fireEvent.click(screen.getByText('set-strong'));

    expect(screen.getByTestId('password').textContent).toBe('Test_Pass_1!');
    expect(screen.getByTestId('isValid').textContent).toBe('true');

    // all rules should be present
    expect(screen.getAllByRole('listitem').length).toBeGreaterThanOrEqual(5);
  });
});
