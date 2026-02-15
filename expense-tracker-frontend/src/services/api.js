/**
 * Centralized API service for all backend calls
 * Handles common fetch configuration, error handling, and JSON parsing
 */

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

/**
 * Custom error class for API errors
 */
export class APIError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.data = data;
  }
}

/**
 * Handle API response
 * Throws APIError if response is not ok
 */
async function handleResponse(response) {
  let data;
  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    throw new APIError(
      data?.message || data?.error || `HTTP ${response.status}`,
      response.status,
      data,
    );
  }

  return data;
}

/**
 * Make a GET request
 */
export async function apiGet(endpoint) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
  });
  return handleResponse(response);
}

/**
 * Make a POST request
 */
export async function apiPost(endpoint, data = null) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: data ? JSON.stringify(data) : undefined,
    credentials: 'include',
  });
  return handleResponse(response);
}

/**
 * Make a PUT request
 */
export async function apiPut(endpoint, data = null) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: data ? JSON.stringify(data) : undefined,
    credentials: 'include',
  });
  return handleResponse(response);
}

/**
 * Make a multipart form data POST request (for file uploads)
 */
export async function apiPostFormData(endpoint, formData) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    body: formData,
    credentials: 'include',
  });
  return handleResponse(response);
}
