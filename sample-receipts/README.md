# Sample Receipts for Demo Testing

This folder contains sample receipt files for testing the receipt upload functionality in the Expense Tracker app.

## Files Included

1. **coffee-receipt.txt** - Coffee shop receipt (Starbucks-style)
2. **grocery-receipt.txt** - Supermarket receipt (Whole Foods-style)
3. **restaurant-receipt.txt** - Restaurant bill (fancy restaurant-style)
4. **gas-receipt.txt** - Gas station receipt (Shell-style)
5. **movie-receipt.txt** - Movie theater receipt (Cinemark-style)
6. **receipt-generator.py** - Python script to generate receipt data URIs

## How to Use in Demo

### Option 1: Upload Text Receipts (Quickest)

1. In the app, click **"Add Expense"**
2. Fill in the details (amount, category, description)
3. Click **"Upload Receipt"**
4. Open one of the `.txt` files in this folder
5. Copy the entire content
6. Paste it in the upload field
7. Submit

### Option 2: Create Receipt Images from Text

If you want image files, use the helper script:

```bash
cd sample-receipts
python3 receipt-generator.py
```

This will create PNG images from the text receipts.

### Option 3: Take Screenshots (Most Realistic)

1. Open a real receipt in your phone/computer
2. Take a screenshot
3. Upload the screenshot in the app

## Quick Demo Script

Want to quickly demo all upload scenarios? Here's a workflow:

1. **Lunch Expense** - Amount: $13.31, Category: Food
2. **Grocery Shopping** - Amount: $84.00, Category: Groceries
3. **Dinner** - Amount: $148.15, Category: Dining
4. **Gas** - Amount: $57.53, Category: Transportation
5. **Entertainment** - Amount: $87.89, Category: Entertainment

Upload the corresponding receipt for each to show the full feature.

## Notes

- In **local demo mode**, uploaded receipts return fake URLs (`local://receipts/...`)
- The receipt files are stored locally in this folder
- No actual files are uploaded to cloud storage
- Perfect for testing the upload UI/UX without cloud infrastructure

---

**Happy Demo Recording!**
