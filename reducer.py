#!/usr/bin/env python3
"""
Reducer: reads sorted (category, amount) pairs from stdin and emits
         (category, total_sales, count) per category.

Input format (tab-separated, sorted by key):
    category    amount

Output format (tab-separated):
    category    total_sales    count
"""

import sys

current_category = None
total_sales = 0.0
count = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    fields = line.split("\t")
    if len(fields) != 2:
        continue

    category, amount = fields[0], fields[1]

    try:
        amount = float(amount)
    except ValueError:
        continue

    if category == current_category:
        total_sales += amount
        count += 1
    else:
        if current_category is not None:
            print(f"{current_category}\t{total_sales:.2f}\t{count}")
        current_category = category
        total_sales = amount
        count = 1

# Emit the last category
if current_category is not None:
    print(f"{current_category}\t{total_sales:.2f}\t{count}")
