import React from 'react';
import PropTypes from 'prop-types';
import { FaEdit, FaTrash } from 'react-icons/fa';

function ExpensesTable({ 
  expenses, 
  loading, 
  categoryFilter, 
  onEditClick, 
  onDeleteClick, 
}) {
  if (loading) return <div>Loading...</div>;
  if (!expenses.length) return <div>No expenses found.</div>;
  return (
    <div className="overflow-x-auto mt-4">
      <table className="dashboard-table w-full border border-[#E5E7EB] rounded-lg overflow-hidden">
        <thead>
          <tr>
            <th className="text-left py-3 px-4 text-[#4B5563] font-semibold text-base border-b border-[#E5E7EB]">
              Amount
            </th>
            <th className="text-left py-3 px-4 text-[#4B5563] font-semibold text-base border-b border-[#E5E7EB]">
              Category
            </th>
            <th className="text-left py-3 px-4 text-[#4B5563] font-semibold text-base border-b border-[#E5E7EB]">
              Description
            </th>
            <th className="text-left py-3 px-4 text-[#4B5563] font-semibold text-base border-b border-[#E5E7EB]">
              Date
            </th>
            <th className="text-left py-3 px-4 text-[#4B5563] font-semibold text-base border-b border-[#E5E7EB]">
              Actions
            </th>
          </tr>
        </thead>
        <tbody>
          {expenses.map((exp) => (
            <tr
              key={exp.id}
              className={
                'border-b border-[#E5E7EB] hover:bg-[#E0F7F4] transition-colors duration-150'
              }
            >
              <td className="py-3 px-4 text-[#10B981] font-semibold">
                ${Number(exp.amount).toFixed(2)}
              </td>
              <td className="py-3 px-4 text-[#9CA3AF]">{exp.category}</td>
              <td className="py-3 px-4 text-[#9CA3AF]">{exp.description}</td>
              <td className="py-3 px-4 text-[#9CA3AF] text-sm">
                {new Date(exp.timestamp).toLocaleDateString()}
              </td>
              <td className="py-3 px-4">
                <div className="flex space-x-2">
                  <button
                    onClick={() => onEditClick(exp)}
                    className="text-blue-500 hover:text-blue-700 transition-colors"
                    aria-label="Edit expense"
                  >
                    <FaEdit />
                  </button>
                  <button
                    onClick={() => onDeleteClick(exp)}
                    className="text-red-500 hover:text-red-700 transition-colors"
                    aria-label="Delete expense"
                  >
                    <FaTrash />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

ExpensesTable.propTypes = {
  expenses: PropTypes.array.isRequired,
  loading: PropTypes.bool,
  categoryFilter: PropTypes.string,
  onEditClick: PropTypes.func.isRequired,
  onDeleteClick: PropTypes.func.isRequired,
};

export default ExpensesTable;
