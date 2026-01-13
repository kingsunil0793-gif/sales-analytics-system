from collections import defaultdict
from typing import List, Dict, Tuple, Any

def calculate_total_revenue(transactions: List[Dict[str, Any]]) -> float:
    return round(sum(t['Quantity'] * t['UnitPrice'] for t in transactions), 2)

def region_wise_sales(transactions: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    stats = defaultdict(lambda: {'sales': 0.0, 'count': 0})
    for t in transactions:
        r = t['Region']
        rev = t['Quantity'] * t['UnitPrice']
        stats[r]['sales'] += rev
        stats[r]['count'] += 1
    total = sum(s['sales'] for s in stats.values())
    result = {}
    for r, s in stats.items():
        perc = round(s['sales'] / total * 100, 2) if total > 0 else 0
        result[r] = {'total_sales': round(s['sales'], 2), 'count': s['count'], 'percentage': perc}
    return dict(sorted(result.items(), key=lambda x: x[1]['total_sales'], reverse=True))

def top_selling_products(transactions: List[Dict[str, Any]], n: int = 5) -> List[Tuple[str, int, float]]:
    stats = defaultdict(lambda: {'qty': 0, 'rev': 0.0})
    for t in transactions:
        name = t['ProductName']
        stats[name]['qty'] += t['Quantity']
        stats[name]['rev'] += t['Quantity'] * t['UnitPrice']
    ranked = [(name, s['qty'], round(s['rev'], 2)) for name, s in stats.items()]
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked[:n]

def customer_analysis(transactions: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    stats = defaultdict(lambda: {'spent': 0.0, 'count': 0, 'products': set()})
    for t in transactions:
        cid = t['CustomerID']
        rev = t['Quantity'] * t['UnitPrice']
        stats[cid]['spent'] += rev
        stats[cid]['count'] += 1
        stats[cid]['products'].add(t['ProductName'])
    result = {}
    for cid, s in stats.items():
        avg = round(s['spent'] / s['count'], 2) if s['count'] > 0 else 0
        result[cid] = {
            'total_spent': round(s['spent'], 2),
            'purchase_count': s['count'],
            'avg_order_value': avg,
            'products_bought': sorted(list(s['products']))
        }
    return dict(sorted(result.items(), key=lambda x: x[1]['total_spent'], reverse=True))

def daily_sales_trend(transactions: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    daily = defaultdict(lambda: {'rev': 0.0, 'count': 0, 'cust': set()})
    for t in transactions:
        d = t['Date']
        rev = t['Quantity'] * t['UnitPrice']
        daily[d]['rev'] += rev
        daily[d]['count'] += 1
        daily[d]['cust'].add(t['CustomerID'])
    result = {}
    for date in sorted(daily):
        s = daily[date]
        result[date] = {
            'revenue': round(s['rev'], 2),
            'transaction_count': s['count'],
            'unique_customers': len(s['cust'])
        }
    return result

def find_peak_sales_day(transactions: List[Dict[str, Any]]) -> Tuple[str, float, int]:
    daily = defaultdict(lambda: {'rev': 0.0, 'count': 0})
    for t in transactions:
        d = t['Date']
        rev = t['Quantity'] * t['UnitPrice']
        daily[d]['rev'] += rev
        daily[d]['count'] += 1
    if not daily:
        return "No data", 0.0, 0
    peak = max(daily.items(), key=lambda x: x[1]['rev'])
    return peak[0], round(peak[1]['rev'], 2), peak[1]['count']

def low_performing_products(transactions: List[Dict[str, Any]], threshold: int = 10) -> List[Tuple[str, int, float]]:
    stats = defaultdict(lambda: {'qty': 0, 'rev': 0.0})
    for t in transactions:
        name = t['ProductName']
        stats[name]['qty'] += t['Quantity']
        stats[name]['rev'] += t['Quantity'] * t['UnitPrice']
    low = [(name, s['qty'], round(s['rev'], 2)) for name, s in stats.items() if s['qty'] < threshold]
    low.sort(key=lambda x: x[1])
    return low
