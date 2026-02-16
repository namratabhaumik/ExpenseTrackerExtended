/**
 * Centralized API service for all backend calls
 * Handles common fetch configuration, error handling, JSON parsing, and CSRF tokens
 * Uses session-based authentication with cookie-to-header CSRF pattern
 */

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

// Cache CSRF token to avoid repeated fetches
let csrfTokenCache = null;

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
 * Clear cached CSRF token (call this after login since Django rotates the token)
 */
export function clearCSRFTokenCache() {
  csrfTokenCache = null;
}

/**
 * Get CSRF token from cookie (Django sets csrftoken cookie)
 */
function getCSRFTokenFromCookie() {
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === 'csrftoken') {
      return decodeURIComponent(value);
    }
  }
  return null;
}

/**
 * Ensure CSRF token cookie is set by making a request to csrf_token_view
 */
async function ensureCSRFTokenCookie() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/csrf-token/`, {
      method: 'GET',
      credentials: 'include',
    });
    // This request triggers Django to set the csrftoken cookie
    return response.ok;
  } catch (error) {
    console.error('Failed to ensure CSRF token cookie:', error);
    return false;
  }
}

/**
 * Fetch and cache CSRF token from server
 */
async function fetchCSRFToken() {
  if (csrfTokenCache) {
    return csrfTokenCache;
  }

  // First, ensure the cookie is set
  await ensureCSRFTokenCookie();

  // Then read from cookie
  const token = getCSRFTokenFromCookie();
  if (token) {
    csrfTokenCache = token;
    return csrfTokenCache;
  }

  // Fallback: try to get from endpoint response (for when cookie reading fails)
  try {
    const response = await fetch(`${API_BASE_URL}/api/csrf-token/`, {
      method: 'GET',
      credentials: 'include',
    });
    const data = await response.json();
    csrfTokenCache = data.csrf_token;
    return csrfTokenCache;
  } catch (error) {
    console.error('Failed to fetch CSRF token:', error);
    return null;
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
 * Get headers for authenticated requests with CSRF token
 */
async function getAuthHeaders(includeCSRF = false) {
  const headers = {
    'Content-Type': 'application/json',
  };

  if (includeCSRF) {
    const token = await fetchCSRFToken();
    if (token) {
      headers['X-CSRFToken'] = token;
    }
  }

  return headers;
}

/**
 * Make a GET request
 */
export async function apiGet(endpoint) {
  const headers = await getAuthHeaders(false);
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'GET',
    headers,
    credentials: 'include',
  });
  return handleResponse(response);
}

/**
 * Make a POST request with CSRF protection
 */
export async function apiPost(endpoint, data = null) {
  const headers = await getAuthHeaders(true);
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers,
    body: data ? JSON.stringify(data) : undefined,
    credentials: 'include',
  });
  return handleResponse(response);
}

/**
 * Make a PUT request with CSRF protection
 */
export async function apiPut(endpoint, data = null) {
  const headers = await getAuthHeaders(true);
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'PUT',
    headers,
    body: data ? JSON.stringify(data) : undefined,
    credentials: 'include',
  });
  return handleResponse(response);
}

/**
 * Make a multipart form data POST request with CSRF protection (for file uploads)
 */
export async function apiPostFormData(endpoint, formData) {
  const token = await fetchCSRFToken();
  const headers = {};
  if (token) {
    headers['X-CSRFToken'] = token;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers,
    body: formData,
    credentials: 'include',
  });
  return handleResponse(response);
}
