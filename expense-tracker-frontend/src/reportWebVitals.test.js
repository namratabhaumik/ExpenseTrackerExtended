import reportWebVitals, { invokeWebVitalsHandlers } from './reportWebVitals';

describe('reportWebVitals', () => {
  test('invokeWebVitalsHandlers calls provided web-vitals functions', () => {
    const handler = jest.fn();
    const mocked = {
      getCLS: jest.fn(),
      getFID: jest.fn(),
      getFCP: jest.fn(),
      getLCP: jest.fn(),
      getTTFB: jest.fn(),
    };

    invokeWebVitalsHandlers(handler, mocked);

    expect(mocked.getCLS).toHaveBeenCalledWith(handler);
    expect(mocked.getFID).toHaveBeenCalledWith(handler);
    expect(mocked.getFCP).toHaveBeenCalledWith(handler);
    expect(mocked.getLCP).toHaveBeenCalledWith(handler);
    expect(mocked.getTTFB).toHaveBeenCalledWith(handler);
  });

  test('reportWebVitals does not throw when no handler is passed', () => {
    expect(() => reportWebVitals()).not.toThrow();
  });
});
