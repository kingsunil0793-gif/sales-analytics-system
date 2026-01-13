# utils/file_handler.py

import re
from typing import List, Dict, Tuple, Optional, Any


def read_sales_data(filename: str = "sales_data.txt") -> List[str]:
    """
    Reads the sales data file with multiple encoding attempts.
    Skips header line and empty lines.
    Returns list of raw transaction lines (strings).
    """
    encodings = ['utf-8', 'latin-1', 'cp1252']

    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding, errors='replace') as f:
                lines = []
                for line in f:
                    stripped = line.strip()
                    if not stripped:
                        continue
                    # Skip header row
                    if 'TransactionID' in stripped and '|' in stripped:
                        continue
                    lines.append(stripped)
            print(f"Successfully read file using encoding: {encoding}")
            print(f"→ Found {len(lines)} potential transaction lines")
            return lines

        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return []
        except UnicodeDecodeError:
            print(f"Encoding '{encoding}' failed, trying next...")
            continue
        except Exception as e:
            print(f"Error reading file with {encoding}: {e}")
            continue

    print("Failed to read file with any supported encoding.")
    return []


def parse_transactions(raw_lines: List[str]) -> List[Dict[str, Any]]:
    """
    Parses raw pipe-delimited lines into list of transaction dictionaries.
    Cleans ProductName (removes commas), converts Quantity to int, UnitPrice to float.
    Skips malformed rows.
    """
    transactions = []

    for line in raw_lines:
        fields = [f.strip() for f in line.split('|')]

        # We expect exactly 8 fields
        if len(fields) != 8:
            continue

        try:
            transaction = {
                'TransactionID': fields[0],
                'Date': fields[1],
                'ProductID': fields[2],
                'ProductName': re.sub(r',\s*', ' ', fields[3]).strip(),   # Mouse,Wireless → Mouse Wireless
                'Quantity': int(re.sub(r'[^0-9-]', '', fields[4])),       # remove commas, keep negative for validation
                'UnitPrice': float(re.sub(r'[^0-9.-]', '', fields[5])),   # remove commas
                'CustomerID': fields[6],
                'Region': fields[7]
            }
            transactions.append(transaction)
        except (ValueError, IndexError):
            # Skip rows with bad number conversion
            continue

    return transactions


def validate_and_filter(
    transactions: List[Dict[str, Any]],
    region: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None
) -> Tuple[List[Dict[str, Any]], int, Dict[str, Any]]:
    """
    Validates transactions according to rules and applies optional filters.
    Prints available regions and amount range.
    Returns: (valid_transactions, invalid_count, summary_dict)
    """
    valid = []
    invalid_count = 0

    # Collect info for user display
    all_regions = set(t['Region'] for t in transactions if t.get('Region'))
    amounts = []
    for t in transactions:
        try:
            amt = t['Quantity'] * t['UnitPrice']
            if amt > 0:  # avoid invalid for display
                amounts.append(amt)
        except:
            pass

    min_possible = min(amounts) if amounts else 0
    max_possible = max(amounts) if amounts else 0

    print("\nAvailable Regions:", ", ".join(sorted(all_regions)) or "None")
    print(f"Transaction Amount Range in data: ₹{min_possible:,.0f} – ₹{max_possible:,.0f}")

    # Counters for filter summary
    filtered_by_region = 0
    filtered_by_amount = 0

    for t in transactions:
        invalid = False

        # Validation rules (REMOVE if invalid)
        if not t['TransactionID'].startswith('T'):
            invalid = True
        if not t['ProductID'].startswith('P'):
            invalid = True
        if not t['CustomerID'].startswith('C'):
            invalid = True
        if t['Quantity'] <= 0:
            invalid = True
        if t['UnitPrice'] <= 0:
            invalid = True
        if not t.get('Region'):
            invalid = True

        if invalid:
            invalid_count += 1
            continue

        # Calculate transaction amount for filtering
        amount = t['Quantity'] * t['UnitPrice']

        # Apply filters
        keep = True

        if region is not None and t['Region'].lower() != region.lower():
            keep = False
            filtered_by_region += 1

        if min_amount is not None and amount < min_amount:
            keep = False
            filtered_by_amount += 1

        if max_amount is not None and amount > max_amount:
            keep = False
            filtered_by_amount += 1

        if keep:
            valid.append(t)

    # Summary dictionary as required
    summary = {
        'total_input': len(transactions),
        'invalid': invalid_count,
        'filtered_by_region': filtered_by_region,
        'filtered_by_amount': filtered_by_amount,
        'final_count': len(valid)
    }

    print("\nValidation & Filter Summary:")
    print(f"  Total input records     : {summary['total_input']}")
    print(f"  Invalid records removed : {summary['invalid']}")
    if region:
        print(f"  Filtered by region      : {summary['filtered_by_region']}")
    if min_amount is not None or max_amount is not None:
        print(f"  Filtered by amount      : {summary['filtered_by_amount']}")
    print(f"  Final valid records     : {summary['final_count']}")

    return valid, invalid_count, summary
