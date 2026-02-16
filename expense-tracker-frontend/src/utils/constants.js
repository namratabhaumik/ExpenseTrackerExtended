/**
 * API Endpoints
 */
export const API_ENDPOINTS = {
  // Auth endpoints
  LOGIN: '/api/login/',
  SIGNUP: '/api/signup/',
  CONFIRM_SIGNUP: '/api/confirm-signup/',
  FORGOT_PASSWORD: '/api/forgot-password/',
  CONFIRM_FORGOT_PASSWORD: '/api/confirm-forgot-password/',

  // Expenses endpoints
  EXPENSES_LIST: '/api/expenses/list/',
  EXPENSES_CREATE: '/api/expenses/',

  // Profile endpoints
  PROFILE: '/api/profile/',
  PROFILE_CHANGE_PASSWORD: '/api/profile/change-password/',

  // Receipt endpoints
  RECEIPTS_UPLOAD: '/api/receipts/upload/',
};

/**
 * Common configuration
 */
export const CONFIG = {
  API_TIMEOUT: 30000,
  MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
  DEFAULT_PAGE_SIZE: 50,
};
