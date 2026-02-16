import React, { useState } from 'react';
import PropTypes from 'prop-types';

function ExpenseFilters({
  sortBy,
  onSortChange,
  categoryFilter,
  onCategoryFilterChange,
  categories,
  totalExpenses,
  onClearFilter,
}) {
  const [showSuggestions, setShowSuggestions] = useState(false);

  const filteredCategorySuggestions = categoryFilter
    ? categories.filter((cat) =>
      cat.toLowerCase().includes(categoryFilter.toLowerCase()),
    )
    : categories;

  return (
    <div className="w-full flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-6">
      <div className="stat-card flex-1 min-w-[220px] flex flex-col items-center md:items-start">
        <span className="text-[#9CA3AF] text-sm font-medium mb-1">
          Total Expenses
        </span>
        <span className="text-4xl font-bold text-[#10B981]">
          ${totalExpenses.toFixed(2)}
        </span>
      </div>
      <div className="flex flex-col md:flex-row gap-2 md:gap-4 items-center relative">
        <label
          className="text-[#4B5563] font-medium text-sm"
          htmlFor="sort-by"
        >
          Sort by:
        </label>
        <select
          id="sort-by"
          className="border border-[#9CA3AF] rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#2563EB] text-[#4B5563] bg-white"
          value={sortBy}
          onChange={(e) => onSortChange(e.target.value)}
        >
          <option value="date_desc">Date (Newest)</option>
          <option value="date_asc">Date (Oldest)</option>
          <option value="amount_desc">Amount (High-Low)</option>
          <option value="amount_asc">Amount (Low-High)</option>
        </select>
        <div className="relative w-full md:w-auto">
          <input
            type="text"
            placeholder="Filter by category"
            className="border border-[#9CA3AF] rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#2563EB] text-[#4B5563] bg-white w-full"
            value={categoryFilter}
            onChange={(e) => {
              onCategoryFilterChange(e.target.value);
              setShowSuggestions(true);
            }}
            onFocus={() => setShowSuggestions(true)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 120)}
            aria-label="Filter by category"
            autoComplete="off"
          />
          {showSuggestions && filteredCategorySuggestions.length > 0 && (
            <ul
              className="absolute z-10 left-0 right-0 bg-white dark:bg-[#23272F] border border-[#9CA3AF] rounded mt-1 max-h-48 overflow-y-auto shadow-lg"
              role="listbox"
            >
              {filteredCategorySuggestions.map((cat) => (
                <li
                  key={cat}
                  role="option"
                  tabIndex={0}
                  className="w-full text-left px-4 py-2 cursor-pointer hover:bg-[#E0F7F4] dark:hover:bg-[#181A20] text-[#4B5563] dark:text-[#F3F4F6]"
                  onMouseDown={() => {
                    onCategoryFilterChange(cat);
                    setShowSuggestions(false);
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      onCategoryFilterChange(cat);
                      setShowSuggestions(false);
                    }
                  }}
                >
                  {cat}
                </li>
              ))}
            </ul>
          )}
        </div>
        {categoryFilter && (
          <button
            onClick={onClearFilter}
            className="text-[#4B5563] hover:text-[#10B981] active:text-[#059669] focus:text-[#10B981] text-sm font-medium transition-colors duration-150"
          >
            Clear Filter
          </button>
        )}
      </div>
    </div>
  );
}

ExpenseFilters.propTypes = {
  sortBy: PropTypes.string.isRequired,
  onSortChange: PropTypes.func.isRequired,
  categoryFilter: PropTypes.string.isRequired,
  onCategoryFilterChange: PropTypes.func.isRequired,
  categories: PropTypes.arrayOf(PropTypes.string).isRequired,
  totalExpenses: PropTypes.number.isRequired,
  onClearFilter: PropTypes.func.isRequired,
};

export default ExpenseFilters;
