import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { ClipLoader } from 'react-spinners';
import { showSuccessToast, showErrorToast } from '../../../utils/toast';

function ReceiptUploadForm() {
  const [receiptFile, setReceiptFile] = useState(null);
  const [receiptFilename, setReceiptFilename] = useState('');
  const [receiptExpenseId, setReceiptExpenseId] = useState('');
  const [receiptStatus, setReceiptStatus] = useState('');
  const [loading, setLoading] = useState(false);

  const handleReceiptFileChange = (e) => {
    setReceiptFile(e.target.files[0]);
    setReceiptFilename(e.target.files[0]?.name || '');
  };

  const handleReceiptUpload = async (e) => {
    e.preventDefault();
    setReceiptStatus('');
    if (!receiptFile) {
      setReceiptStatus('Please select a file.');
      showErrorToast('Please select a file.', {
        position: 'top-right',
        style: {
          background: '#fee2e2',
          color: '#4B5563',
          borderRadius: 8,
          fontWeight: 500,
        },
        progressStyle: { background: '#ef4444' },
      });
      return;
    }
    setLoading(true);
    // Read file as base64
    const reader = new window.FileReader();
    reader.onload = async () => {
      const base64Data = reader.result.split(',')[1];
      const payload = {
        file: base64Data,
        filename: receiptFilename,
      };
      if (receiptExpenseId) payload.expense_id = receiptExpenseId;
      try {
        const resp = await fetch(
          `${process.env.REACT_APP_BACKEND_URL}/api/receipts/upload/`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(payload),
          },
        );
        const data = await resp.json();
        if (!resp.ok) {
          setReceiptStatus(data.error || 'Failed to upload receipt');
          showErrorToast(data.error || 'Failed to upload receipt', {
            position: 'top-right',
            style: {
              background: '#fee2e2',
              color: '#4B5563',
              borderRadius: 8,
              fontWeight: 500,
            },
            progressStyle: { background: '#ef4444' },
          });
        } else {
          setReceiptStatus('Receipt uploaded successfully!');
          setReceiptFile(null);
          setReceiptFilename('');
          setReceiptExpenseId('');
          showSuccessToast('Receipt uploaded successfully!', {
            position: 'top-right',
            style: {
              background: '#d1fae5',
              color: '#2563EB',
              borderRadius: 8,
              fontWeight: 500,
            },
            progressStyle: { background: '#10b981' },
          });
        }
      } catch (e) {
        setReceiptStatus('An error occurred while uploading receipt.');
        showErrorToast('An error occurred while uploading receipt.', {
          position: 'top-right',
          style: {
            background: '#fee2e2',
            color: '#4B5563',
            borderRadius: 8,
            fontWeight: 500,
          },
          progressStyle: { background: '#ef4444' },
        });
      } finally {
        setLoading(false);
      }
    };
    reader.readAsDataURL(receiptFile);
  };

  return (
    <>
      <h3>Upload Receipt</h3>
      <form className="expenses-receipt-form" onSubmit={handleReceiptUpload}>
        <input
          type="file"
          accept="image/*,.pdf"
          onChange={handleReceiptFileChange}
          disabled={loading}
        />
        <input
          type="text"
          placeholder="Filename (optional)"
          value={receiptFilename}
          onChange={(e) => setReceiptFilename(e.target.value)}
          disabled={loading}
        />
        <input
          type="text"
          placeholder="Expense ID (optional)"
          value={receiptExpenseId}
          onChange={(e) => setReceiptExpenseId(e.target.value)}
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
      {receiptStatus && (
        <p
          className={
            receiptStatus.includes('success')
              ? 'expenses-success'
              : 'expenses-error'
          }
        >
          {receiptStatus}
        </p>
      )}
    </>
  );
}

ReceiptUploadForm.propTypes = {};

export default ReceiptUploadForm;
