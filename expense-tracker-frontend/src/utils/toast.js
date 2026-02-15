import { toast } from 'react-toastify';

const defaultOptions = {
  position: 'top-right',
  autoClose: 3000,
  hideProgressBar: false,
  closeOnClick: true,
  pauseOnHover: true,
  draggable: true,
};

/**
 * Show success toast notification
 */
export function showSuccessToast(message) {
  toast.success(message, {
    ...defaultOptions,
    style: {
      backgroundColor: '#d4edda',
      color: '#155724',
      borderLeft: '4px solid #28a745',
    },
  });
}

/**
 * Show error toast notification
 */
export function showErrorToast(message) {
  toast.error(message, {
    ...defaultOptions,
    style: {
      backgroundColor: '#f8d7da',
      color: '#721c24',
      borderLeft: '4px solid #dc3545',
    },
  });
}

/**
 * Show info toast notification
 */
export function showInfoToast(message) {
  toast.info(message, {
    ...defaultOptions,
    style: {
      backgroundColor: '#d1ecf1',
      color: '#0c5460',
      borderLeft: '4px solid #17a2b8',
    },
  });
}

/**
 * Show warning toast notification
 */
export function showWarningToast(message) {
  toast.warning(message, {
    ...defaultOptions,
    style: {
      backgroundColor: '#fff3cd',
      color: '#856404',
      borderLeft: '4px solid #ffc107',
    },
  });
}
