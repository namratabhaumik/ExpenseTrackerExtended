import React from 'react';
import PropTypes from 'prop-types';
import { ClipLoader } from 'react-spinners';

function UploadReceiptForm({
  receiptFile,
  receiptFilename,
  receiptExpenseId,
  receiptStatus,
  loading,
  onFileChange,
  onFilenameChange,
  onExpenseIdChange,
  onSubmit,
}) {
  return (
    <form className="expenses-receipt-form" onSubmit={onSubmit}>
      <input
        type="file"
        aria-label="receipt-file"
        accept="image/*,.pdf"
        onChange={onFileChange}
        disabled={loading}
      />
      <input
        type="text"
        placeholder="Filename (optional)"
        value={receiptFilename}
        onChange={onFilenameChange}
        disabled={loading}
      />
      <input
        type="text"
        placeholder="Expense ID (optional)"
        value={receiptExpenseId}
        onChange={onExpenseIdChange}
        disabled={loading}
      />
      <button
        type="submit"
        disabled={loading}
        className="flex items-center justify-center gap-2"
      >
        {loading ? <ClipLoader size={20} color="#fff" /> : 'Upload'}
      </button>

    </form>
  );
}

UploadReceiptForm.propTypes = {
  receiptFile: PropTypes.object,
  receiptFilename: PropTypes.string,
  receiptExpenseId: PropTypes.string,
  receiptStatus: PropTypes.string,
  loading: PropTypes.bool,
  onFileChange: PropTypes.func.isRequired,
  onFilenameChange: PropTypes.func.isRequired,
  onExpenseIdChange: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
};

export default UploadReceiptForm;
