# Sample Receipts Generator

Utility for generating random text-based receipts for testing the receipt upload functionality in the Expense Tracker app.

## Files

- **receipt-generator.py** - Generates a random receipt each time you run it

## Usage

Generate a random receipt and print to stdout:

```bash
python3 receipt-generator.py
```

Example output:
```
==================================================
          Whole Foods Market
        (Grocery Store)
==================================================

Date: 02/10/2026
Time: 03:45 PM
Location: Store #4521

--------------------------------------------------
ITEMS:
--------------------------------------------------
Organic Coffee Beans       x2 $   25.98
Fresh Vegetables           x1 $    8.50
Bread                      x3 $    8.97
--------------------------------------------------
SUBTOTAL                           $   43.45
TAX (8%)                           $    3.48
==================================================
TOTAL                              $   46.93
==================================================

Thank you for your purchase!
Please come again.
```

## How to Use for Testing

### Quick Upload

1. Run the generator: `python3 receipt-generator.py`
2. Copy the output
3. In the app, click **"Add Expense"** → **"Upload Receipt"**
4. Paste the receipt text
5. Submit

### Save to File

```bash
python3 receipt-generator.py > receipt.txt
```

## Notes

- Each run generates a different random receipt with realistic data
- Receipts include various merchants (groceries, restaurants, pharmacies, etc.)
- Items and amounts are randomized
- Tax calculated at 8%
- Perfect for testing without actual images

---

**Ready to test!**
