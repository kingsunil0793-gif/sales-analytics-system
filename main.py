# main.py
# ────────────────────────────────────────────────────────────────
# Complete Sales Analytics System – Modular version
# Uses only the three required utils modules
# Report generation is embedded here (no separate report_generator.py)
# Input file: data/sales_data.txt (as per checklist)
# Output: data/enriched_sales_data.txt and output/sales_report.txt
# ────────────────────────────────────────────────────────────────

import os
import sys
from datetime import datetime
from collections import defaultdict

# Import the three required modules from utils/
from utils.file_handler import read_sales_data, parse_transactions, validate_and_filter
from utils.data_processor import (
    calculate_total_revenue,
    region_wise_sales,
    top_selling_products,
    customer_analysis
)
from utils.api_handler import fetch_all_products, create_product_mapping, enrich_sales_data, save_enriched_data


def print_step(step: int, message: str, success=True, extra=""):
    mark = "✓" if success else "✗"
    print(f"[{step}/9] {message.ljust(30)} {mark} {extra}")


def generate_sales_report(
    transactions: list[dict],
    enriched_transactions: list[dict],
    output_file: str = "output/sales_report.txt"
):
    """
    Generates the comprehensive report with all required sections.
    Embedded in main.py since no separate module was specified.
    """
    if not transactions:
        print("No data to generate report.")
        return

    total_revenue = sum(t['Quantity'] * t['UnitPrice'] for t in transactions)
    total_transactions = len(transactions)
    avg_order_value = total_revenue / total_transactions if total_transactions > 0 else 0

    dates = [t['Date'] for t in transactions if t.get('Date')]
    date_min = min(dates) if dates else "N/A"
    date_max = max(dates) if dates else "N/A"

    # Region-wise
    region_stats = defaultdict(lambda: {'sales': 0.0, 'count': 0})
    for t in transactions:
        reg = t['Region']
        rev = t['Quantity'] * t['UnitPrice']
        region_stats[reg]['sales'] += rev
        region_stats[reg]['count'] += 1

    grand_total = total_revenue
    region_list = sorted(
        [(r, round(s['sales'], 2), round(s['sales'] / grand_total * 100, 2) if grand_total > 0 else 0, s['count'])
         for r, s in region_stats.items()],
        key=lambda x: x[1], reverse=True
    )

    # Top 5 products by quantity
    prod_stats = defaultdict(lambda: {'qty': 0, 'rev': 0.0})
    for t in transactions:
        name = t['ProductName']
        prod_stats[name]['qty'] += t['Quantity']
        prod_stats[name]['rev'] += t['Quantity'] * t['UnitPrice']

    top_products = sorted(
        [(name, s['qty'], round(s['rev'], 2)) for name, s in prod_stats.items()],
        key=lambda x: x[1], reverse=True
    )[:5]

    # API enrichment summary
    enriched_count = sum(1 for t in enriched_transactions if t.get('API_Match', False))
    success_rate = round(enriched_count / len(enriched_transactions) * 100, 1) if enriched_transactions else 0
    unmatched = set(t['ProductName'] for t in enriched_transactions if not t.get('API_Match', False))

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("           SALES ANALYTICS REPORT\n")
        f.write(f"     Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"     Records Processed: {total_transactions}\n")
        f.write("=" * 60 + "\n\n")

        f.write("OVERALL SUMMARY\n")
        f.write("-" * 40 + "\n")
        f.write(f"Total Revenue          : ₹{total_revenue:,.2f}\n")
        f.write(f"Total Transactions     : {total_transactions:,}\n")
        f.write(f"Average Order Value    : ₹{avg_order_value:,.2f}\n")
        f.write(f"Date Range             : {date_min} to {date_max}\n\n")

        f.write("REGION-WISE PERFORMANCE\n")
        f.write("-" * 40 + "\n")
        f.write(f"{'Region':<12} {'Sales Amount':>15} {'% of Total':>12} {'Transactions':>12}\n")
        f.write("-" * 55 + "\n")
        for reg, sales, perc, cnt in region_list:
            f.write(f"{reg:<12} ₹{sales:>14,.2f} {perc:>11.2f}% {cnt:>12}\n")
        f.write("\n")

        f.write("TOP 5 PRODUCTS BY QUANTITY SOLD\n")
        f.write("-" * 40 + "\n")
        f.write(f"{'Rank':<6} {'Product Name':<28} {'Qty Sold':>10} {'Revenue':>15}\n")
        f.write("-" * 65 + "\n")
        for i, (name, qty, rev) in enumerate(top_products, 1):
            f.write(f"{i:<6} {name:<28} {qty:>10,} ₹{rev:>14,.2f}\n")
        f.write("\n")

        f.write("API ENRICHMENT SUMMARY\n")
        f.write("-" * 40 + "\n")
        f.write(f"Total processed transactions : {len(enriched_transactions)}\n")
        f.write(f"Successfully enriched        : {enriched_count}\n")
        f.write(f"Success rate                 : {success_rate}%\n")
        if unmatched:
            f.write("\nProducts not found in API:\n")
            for p in sorted(unmatched)[:10]:
                f.write(f"  • {p}\n")
            if len(unmatched) > 10:
                f.write(f"  ... (+{len(unmatched)-10} more)\n")

    print(f"Report successfully generated: {output_file}")


def main():
    print("=" * 50)
    print("     SALES ANALYTICS SYSTEM")
    print("=" * 50)
    print()

    try:
        print_step(1, "Reading sales data...")
        raw_lines = read_sales_data()  # reads from data/sales_data.txt
        print_step(1, f"Found {len(raw_lines)} lines")

        print_step(2, "Parsing transactions...")
        parsed = parse_transactions(raw_lines)
        print_step(2, f"Parsed {len(parsed)} records")

        print_step(3, "Showing filter options...")
        valid, invalid_count, _ = validate_and_filter(parsed)

        choice = input("\nDo you want to apply filters? (y/n): ").strip().lower()
        if choice in ('y', 'yes'):
            region = input("  Region (leave blank to skip): ").strip() or None
            min_a = input("  Min amount (leave blank to skip): ").strip()
            max_a = input("  Max amount (leave blank to skip): ").strip()
            min_amount = float(min_a) if min_a else None
            max_amount = float(max_a) if max_a else None
            valid, invalid_count, _ = validate_and_filter(parsed, region, min_amount, max_amount)

        print_step(4, f"Validated → {len(valid)} valid, {invalid_count} invalid")

        print_step(5, "Fetching product data from API...")
        api_products = fetch_all_products()
        print_step(5, f"Fetched {len(api_products)} products")

        print_step(6, "Enriching sales data...")
        mapping = create_product_mapping(api_products)
        enriched = enrich_sales_data(valid, mapping)
        match_count = sum(1 for t in enriched if t.get('API_Match', False))
        rate = round(match_count / len(enriched) * 100, 1) if enriched else 0
        print_step(6, f"Enriched {match_count}/{len(enriched)} ({rate}%)")

        print_step(7, "Saving enriched data...")
        save_enriched_data(enriched)
        print_step(7, "Saved to data/enriched_sales_data.txt")

        print_step(8, "Generating report...")
        generate_sales_report(valid, enriched)
        print_step(8, "Saved to output/sales_report.txt")

        print_step(9, "Process Complete!")
        print("=" * 50)
        print("Output files:")
        print("  • data/enriched_sales_data.txt")
        print("  • output/sales_report.txt")
        print("=" * 50)

    except Exception as e:
        print("\n" + "=" * 50)
        print("ERROR:", str(e))
        print("Check file path, internet, or data format.")
        print("=" * 50)
        sys.exit(1)


if __name__ == "__main__":
    main()
