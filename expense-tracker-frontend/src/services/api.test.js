import { apiGet, apiPost, apiPut, apiPostFormData, APIError } from './api';

describe('api helpers', () => {
  const OLD = global.fetch;

  afterEach(() => {
    global.fetch = OLD;
    jest.resetAllMocks();
  });

  test('apiGet returns parsed json on ok response', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ hello: 'world' }),
    });

    const res = await apiGet('/test');
    expect(res).toEqual({ hello: 'world' });
    expect(global.fetch).toHaveBeenCalled();
  });

  test('apiPost throws APIError on non-ok', async () => {
    let callCount = 0;
    global.fetch = jest.fn().mockImplementation(() => {
      callCount += 1;
      // First call is for CSRF token fetch
      if (callCount === 1) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ csrf_token: 'test-token' }),
        });
      }
      // Second call is the actual POST request
      return Promise.resolve({
        ok: false,
        status: 400,
        json: async () => ({ message: 'bad request' }),
      });
    });

    await expect(apiPost('/x', { a: 1 })).rejects.toThrow(APIError);
    await expect(apiPost('/x', { a: 1 })).rejects.toMatchObject({ status: 400 });
  });

  test('apiPut handles invalid JSON body gracefully (returns null)', async () => {
    let callCount = 0;
    global.fetch = jest.fn().mockImplementation(() => {
      callCount += 1;
      // First call is for CSRF token fetch
      if (callCount === 1) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ csrf_token: 'test-token' }),
        });
      }
      // Second call is the actual PUT request
      return Promise.resolve({
        ok: true,
        json: async () => { throw new Error('no json'); },
      });
    });

    const res = await apiPut('/empty');
    expect(res).toBeNull();
  });

  test('apiPostFormData sends FormData body and returns data', async () => {
    let callCount = 0;
    global.fetch = jest.fn().mockImplementation((_url, opts) => {
      callCount += 1;
      // First call is for CSRF token fetch
      if (callCount === 1) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ csrf_token: 'test-token' }),
        });
      }
      // Second call is the actual POST request
      expect(opts.method).toBe('POST');
      // should have CSRF token in headers
      expect(opts.headers).toEqual({ 'X-CSRFToken': 'test-token' });
      return Promise.resolve({ ok: true, json: async () => ({ ok: true }) });
    });

    const fd = new FormData();
    fd.append('file', 'dummy');

    const r = await apiPostFormData('/upload', fd);
    expect(r).toEqual({ ok: true });
  });
});
