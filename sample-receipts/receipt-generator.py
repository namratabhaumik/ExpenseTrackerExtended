#!/usr/bin/env python3
"""
Receipt Generator Utility
Converts sample receipt text files into various formats for testing.
"""

import os
import base64
import json
from pathlib import Path

def get_receipt_files():
    """Get all receipt text files in this directory."""
    current_dir = Path(__file__).parent
    receipts = sorted(current_dir.glob('*-receipt.txt'))
    return receipts

def read_receipt(filepath):
    """Read receipt file content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def create_base64_data_uri(filepath):
    """Create base64 encoded data URI from receipt text."""
    content = read_receipt(filepath)
    # Encode as UTF-8 bytes, then base64
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    return f"data:text/plain;base64,{encoded}"

def create_json_export(filepath):
    """Create JSON export of receipt."""
    filename = Path(filepath).stem
    content = read_receipt(filepath)

    # Extract key info from receipt (simple parsing)
    lines = content.split('\n')
    total = None
    date = None
    location = None

    for line in lines:
        if 'TOTAL' in line and '$' in line:
            total = line.split('$')[-1].strip()
        elif 'Date:' in line:
            date = line.split('Date:')[-1].split('Time:')[0].strip()
        elif 'Location:' in line:
            location = line.split('Location:')[-1].strip()

    return {
        'filename': filename,
        'name': filename.replace('-', ' ').title(),
        'total': total,
        'date': date,
        'location': location,
        'content': content
    }

def main():
    """Generate receipt formats."""
    print("\n" + "="*50)
    print("  Receipt Generator - Demo Testing Utility")
    print("="*50 + "\n")

    receipts = get_receipt_files()

    if not receipts:
        print("No receipt files found!")
        return

    print(f"Found {len(receipts)} receipt files:\n")

    for i, receipt_file in enumerate(receipts, 1):
        filename = receipt_file.name
        print(f"{i}. {filename}")

    print("\n" + "-"*50)
    print("\nGenerated Formats:")
    print("-"*50 + "\n")

    # Generate Base64 URIs
    print("BASE64 DATA URIs (for direct upload):\n")
    for receipt_file in receipts:
        uri = create_base64_data_uri(receipt_file)
        print(f"\n{receipt_file.stem}:")
        print(f"  URI Length: {len(uri)} chars")
        print(f"  URI Preview: {uri[:80]}...")

    # Generate JSON export
    print("\n\nJSON EXPORTS:\n")
    json_data = []
    for receipt_file in receipts:
        data = create_json_export(receipt_file)
        json_data.append(data)
        print(f"  {data['name']} - ${data['total']} ({data['date']})")

    # Save JSON export
    output_file = Path(__file__).parent / 'receipts.json'
    with open(output_file, 'w') as f:
        json.dump(json_data, f, indent=2)

    print(f"\n  Exported to: {output_file.name}")

    print("\n" + "-"*50)
    print("\nUsage Instructions:")
    print("-"*50)
    print("""
1. For Text Upload (Quickest for Demo):
   - Copy content from any *-receipt.txt file
   - Paste in the app's receipt upload field

2. For Base64 Data URIs:
   - Use the generated data URIs above
   - These can be used programmatically in tests

3. For JSON Testing:
   - Load receipts.json in your test suite
   - Automated receipt upload testing

Examples:
   $ python3 receipt-generator.py          # Show this output
   $ cat coffee-receipt.txt                # View receipt
   $ cat receipts.json | jq '.[0]'         # View first receipt JSON
    """)

    print("="*50)
    print("Ready for demo!\n")

if __name__ == '__main__':
    main()
