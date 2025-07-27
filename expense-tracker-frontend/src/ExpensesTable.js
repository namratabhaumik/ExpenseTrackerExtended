import React from 'react';
import PropTypes from 'prop-types';

function ExpensesTable({ expenses, loading, categoryFilter }) {
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
};

export default ExpensesTable;
