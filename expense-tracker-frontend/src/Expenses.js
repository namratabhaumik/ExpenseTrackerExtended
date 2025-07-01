import React, { useEffect, useState } from "react";

function Expenses({ onLogout, accessToken }) {
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    amount: "",
    category: "",
    description: "",
  });
  const [addError, setAddError] = useState("");
  const [addSuccess, setAddSuccess] = useState("");
  // Receipt upload state
  const [receiptFile, setReceiptFile] = useState(null);
  const [receiptFilename, setReceiptFilename] = useState("");
  const [receiptExpenseId, setReceiptExpenseId] = useState("");
  const [receiptStatus, setReceiptStatus] = useState("");
  const [receiptUrl, setReceiptUrl] = useState("");

  // Fetch expenses on mount
  useEffect(() => {
    const fetchExpenses = async () => {
      setLoading(true);
      setError("");
      try {
        const resp = await fetch(
          `${process.env.REACT_APP_BACKEND_URL}/api/expenses/list/`,
          {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
            credentials: "include",
          }
        );
        if (!resp.ok) {
          const err = await resp.json();
          setError(err.error || "Failed to fetch expenses");
          setExpenses([]);
        } else {
          const data = await resp.json();
          setExpenses(data.expenses || []);
        }
      } catch (e) {
        setError("An error occurred while fetching expenses.");
        setExpenses([]);
      } finally {
        setLoading(false);
      }
    };
    if (accessToken) fetchExpenses();
  }, [accessToken]);

  // Handle form input
  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // Handle add expense
  const handleAddExpense = async (e) => {
    e.preventDefault();
    setAddError("");
    setAddSuccess("");
    try {
      const resp = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/expenses/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
          credentials: "include",
          body: JSON.stringify(form),
        }
      );
      if (!resp.ok) {
        const err = await resp.json();
        setAddError(err.error || "Failed to add expense");
      } else {
        setAddSuccess("Expense added successfully!");
        setForm({ amount: "", category: "", description: "" });
        // Refresh expenses
        const data = await resp.json();
        setExpenses((prev) => [data.expense, ...prev]);
      }
    } catch (e) {
      setAddError("An error occurred while adding expense.");
    }
  };

  // Handle receipt file change
  const handleReceiptFileChange = (e) => {
    setReceiptFile(e.target.files[0]);
    setReceiptFilename(e.target.files[0]?.name || "");
  };

  // Handle receipt upload
  const handleReceiptUpload = async (e) => {
    e.preventDefault();
    setReceiptStatus("");
    setReceiptUrl("");
    if (!receiptFile) {
      setReceiptStatus("Please select a file.");
      return;
    }
    // Read file as base64
    const reader = new FileReader();
    reader.onload = async () => {
      const base64Data = reader.result.split(",")[1];
      const payload = {
        file: base64Data,
        filename: receiptFilename,
      };
      if (receiptExpenseId) payload.expense_id = receiptExpenseId;
      try {
        const resp = await fetch(
          `${process.env.REACT_APP_BACKEND_URL}/api/receipts/upload/`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${accessToken}`,
            },
            credentials: "include",
            body: JSON.stringify(payload),
          }
        );
        const data = await resp.json();
        if (!resp.ok) {
          setReceiptStatus(data.error || "Failed to upload receipt");
        } else {
          setReceiptStatus("Receipt uploaded successfully!");
          setReceiptFile(null);
          setReceiptFilename("");
          setReceiptExpenseId("");
        }
      } catch (e) {
        setReceiptStatus("An error occurred while uploading receipt.");
      }
    };
    reader.readAsDataURL(receiptFile);
  };

  return (
    <div>
      <h2>Expenses</h2>
      <button onClick={onLogout}>Logout</button>
      <h3>Add Expense</h3>
      <form onSubmit={handleAddExpense}>
        <input
          type="number"
          name="amount"
          placeholder="Amount"
          value={form.amount}
          onChange={handleChange}
          required
        />
        <input
          type="text"
          name="category"
          placeholder="Category"
          value={form.category}
          onChange={handleChange}
          required
        />
        <input
          type="text"
          name="description"
          placeholder="Description"
          value={form.description}
          onChange={handleChange}
        />
        <button type="submit">Add</button>
      </form>
      {addError && <p style={{ color: "red" }}>{addError}</p>}
      {addSuccess && <p style={{ color: "green" }}>{addSuccess}</p>}
      <h3>Upload Receipt</h3>
      <form onSubmit={handleReceiptUpload}>
        <input
          type="file"
          accept="image/*,.pdf"
          onChange={handleReceiptFileChange}
        />
        <input
          type="text"
          placeholder="Filename (optional)"
          value={receiptFilename}
          onChange={(e) => setReceiptFilename(e.target.value)}
        />
        <input
          type="text"
          placeholder="Expense ID (optional)"
          value={receiptExpenseId}
          onChange={(e) => setReceiptExpenseId(e.target.value)}
        />
        <button type="submit">Upload</button>
      </form>
      {receiptStatus && (
        <p
          style={{ color: receiptStatus.includes("success") ? "green" : "red" }}
        >
          {receiptStatus}
        </p>
      )}
      <h3>Your Expenses</h3>
      {loading ? (
        <p>Loading...</p>
      ) : error ? (
        <p style={{ color: "red" }}>{error}</p>
      ) : expenses.length === 0 ? (
        <p>No expenses found.</p>
      ) : (
        <table style={{ margin: "0 auto" }}>
          <thead>
            <tr>
              <th>Amount</th>
              <th>Category</th>
              <th>Description</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {expenses.map((exp) => (
              <tr key={exp.id}>
                <td>{exp.amount}</td>
                <td>{exp.category}</td>
                <td>{exp.description}</td>
                <td>{new Date(exp.timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default Expenses;
