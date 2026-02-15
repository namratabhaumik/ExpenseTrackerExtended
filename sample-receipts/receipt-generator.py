#!/usr/bin/env python3
"""
Random Receipt Generator Utility
Generates random text-based receipt files for testing.
"""

import random
import json
from datetime import datetime, timedelta
from pathlib import Path

# Sample data for realistic receipts
MERCHANTS = [
    ("Whole Foods Market", "Grocery Store"),
    ("Starbucks Coffee", "Coffee Shop"),
    ("Target Store", "Retail"),
    ("Best Buy", "Electronics"),
    ("CVS Pharmacy", "Pharmacy"),
    ("Chipotle Mexican Grill", "Restaurant"),
    ("Amazon Fresh", "Grocery"),
    ("Walgreens", "Pharmacy"),
    ("Home Depot", "Hardware"),
    ("Trader Joe's", "Grocery Store"),
]

ITEMS = [
    ("Organic Coffee Beans", 12.99),
    ("Fresh Vegetables", 8.50),
    ("Eggs (Dozen)", 4.99),
    ("Milk (1L)", 3.49),
    ("Bread", 2.99),
    ("Cheese", 5.99),
    ("Coffee (Grande)", 5.45),
    ("Sandwich", 9.99),
    ("Phone Case", 24.99),
    ("USB Cable", 15.99),
    ("Shampoo", 7.49),
    ("Toothpaste", 3.99),
]

def generate_receipt():
    """Generate a random receipt."""
    merchant, merchant_type = random.choice(MERCHANTS)

    # Generate random date in last 30 days
    days_ago = random.randint(0, 30)
    receipt_date = datetime.now() - timedelta(days=days_ago)

    # Generate random items
    num_items = random.randint(2, 7)
    items = random.sample(ITEMS, min(num_items, len(ITEMS)))

    # Calculate totals
    subtotal = sum(price for _, price in items)
    tax = round(subtotal * 0.08, 2)  # 8% tax
    total = round(subtotal + tax, 2)

    # Build receipt text
    receipt_lines = [
        "=" * 50,
        f"{merchant.center(50)}",
        f"({merchant_type})".center(50),
        "=" * 50,
        "",
        f"Date: {receipt_date.strftime('%m/%d/%Y')}",
        f"Time: {receipt_date.strftime('%I:%M %p')}",
        f"Location: Store #{random.randint(100, 9999)}",
        "",
        "-" * 50,
        "ITEMS:",
        "-" * 50,
    ]

    for item_name, price in items:
        qty = random.randint(1, 3)
        line_total = round(price * qty, 2)
        receipt_lines.append(f"{item_name:<35} x{qty:>1} ${line_total:>8.2f}")

    receipt_lines.extend([
        "-" * 50,
        f"{'SUBTOTAL':<42} ${subtotal:>8.2f}",
        f"{'TAX (8%)':<42} ${tax:>8.2f}",
        "=" * 50,
        f"{'TOTAL':<42} ${total:>8.2f}",
        "=" * 50,
        "",
        "Thank you for your purchase!",
        "Please come again.",
        "",
    ])

    return "\n".join(receipt_lines), {
        "merchant": merchant,
        "date": receipt_date.strftime('%m/%d/%Y'),
        "time": receipt_date.strftime('%I:%M %p'),
        "subtotal": subtotal,
        "tax": tax,
        "total": total,
    }

def main():
    """Generate a random receipt and print to stdout."""
    receipt_text, metadata = generate_receipt()
    print(receipt_text)

if __name__ == '__main__':
    main()
