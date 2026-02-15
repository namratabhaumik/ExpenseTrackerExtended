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
    global.fetch = jest.fn().mockResolvedValue({
      ok: false,
      status: 400,
      json: async () => ({ message: 'bad request' }),
    });

    await expect(apiPost('/x', { a: 1 })).rejects.toThrow(APIError);
    await expect(apiPost('/x', { a: 1 })).rejects.toMatchObject({ status: 400 });
  });

  test('apiPut handles invalid JSON body gracefully (returns null)', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => { throw new Error('no json'); },
    });

    const res = await apiPut('/empty');
    expect(res).toBeNull();
  });

  test('apiPostFormData sends FormData body and returns data', async () => {
    const fd = new FormData();
    fd.append('file', 'dummy');

    global.fetch = jest.fn().mockImplementation((url, opts) => {
      expect(opts.method).toBe('POST');
      // should not set JSON content-type for form data
      expect(opts.headers).toBeUndefined();
      return Promise.resolve({ ok: true, json: async () => ({ ok: true }) });
    });

    const r = await apiPostFormData('/upload', fd);
    expect(r).toEqual({ ok: true });
  });
});
