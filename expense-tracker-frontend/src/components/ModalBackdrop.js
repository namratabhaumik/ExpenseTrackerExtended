import React from 'react';
import PropTypes from 'prop-types';

const ModalBackdrop = ({ children, show, onClose, onKeyDown }) => {
  if (!show) return null;

  const handleBackdropKeyDown = (e) => {
    // Call the passed onKeyDown handler if it exists
    onKeyDown?.(e);
    
    // Also handle Escape key if onClose is provided
    if (e.key === 'Escape' && onClose && !e.defaultPrevented) {
      onClose();
    }
  };

  const handleClick = (e) => {
    // Don't close if clicking inside the modal content
    if (!e.target.closest('[role="dialog"]') && onClose) {
      onClose();
    }
  };

  return (
    <div 
      className="fixed inset-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center z-50 cursor-default"
      onKeyDown={handleBackdropKeyDown}
      onClick={handleClick}
      role="button"
      tabIndex={0}
      aria-label="Close modal"
    >
      <div 
        role="presentation"
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-full"
      >
        {children}
      </div>
    </div>
  );
};

ModalBackdrop.propTypes = {
  children: PropTypes.node.isRequired,
  show: PropTypes.bool.isRequired,
  onClose: PropTypes.func,
  onKeyDown: PropTypes.func,
};

ModalBackdrop.defaultProps = {
  onClose: undefined,
  onKeyDown: undefined,
};

export default ModalBackdrop;
