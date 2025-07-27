import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import UploadReceiptForm from './UploadReceiptForm';

// Mock ClipLoader to keep DOM clean
jest.mock('react-spinners', () => ({
  ClipLoader: () => <span data-testid="clip-loader" />,
}));

describe('UploadReceiptForm component', () => {
  const baseProps = {
    receiptFile: null,
    receiptFilename: 'receipt.jpg',
    receiptExpenseId: 'exp123',
    receiptStatus: '',
    loading: false,
    onFileChange: jest.fn(),
    onFilenameChange: jest.fn(),
    onExpenseIdChange: jest.fn(),
    onSubmit: jest.fn((e) => e.preventDefault()),
  };

  test('renders inputs with provided values', () => {
    render(<UploadReceiptForm {...baseProps} />);

    expect(screen.getByPlaceholderText('Filename (optional)')).toHaveValue(
      baseProps.receiptFilename,
    );
    expect(screen.getByPlaceholderText('Expense ID (optional)')).toHaveValue(
      baseProps.receiptExpenseId,
    );
  });

  test('calls change handlers when inputs are modified', () => {
    render(<UploadReceiptForm {...baseProps} />);

    fireEvent.change(screen.getByPlaceholderText('Filename (optional)'), {
      target: { value: 'newname.png' },
    });
    fireEvent.change(screen.getByPlaceholderText('Expense ID (optional)'), {
      target: { value: 'exp999' },
    });

    expect(baseProps.onFilenameChange).toHaveBeenCalledTimes(1);
    expect(baseProps.onExpenseIdChange).toHaveBeenCalledTimes(1);
  });

  test('fires onFileChange when a file is selected', () => {
    render(<UploadReceiptForm {...baseProps} />);

    const fileInput = screen.getByLabelText('receipt-file');
    const file = new File(['dummy'], 'dummy.png', { type: 'image/png' });
    fireEvent.change(fileInput, { target: { files: [file] } });

    expect(baseProps.onFileChange).toHaveBeenCalledTimes(1);
  });

  test('calls onSubmit on form submission', () => {
    render(<UploadReceiptForm {...baseProps} />);

    fireEvent.submit(screen.getByRole('button', { name: /upload/i }));
    expect(baseProps.onSubmit).toHaveBeenCalledTimes(1);
  });

  test('disables inputs and shows loader when loading', () => {
    render(<UploadReceiptForm {...baseProps} loading />);

    expect(screen.getByPlaceholderText('Filename (optional)')).toBeDisabled();
    expect(screen.getByTestId('clip-loader')).toBeInTheDocument();
  });
});
