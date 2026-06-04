#!/usr/bin/env python3
"""
Mapper: reads purchases from stdin and emits (category, amount) pairs.

Input format (tab-separated):
    date    time    city    category    amount    payment_method

Output format (tab-separated):
    category    amount
"""

import sys

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    fields = line.split("\t")
    if len(fields) < 5:
        continue  # skip malformed lines

    category = fields[3]
    amount = fields[4]

    try:
        amount = float(amount)
    except ValueError:
        continue  # skip lines with invalid amounts

    print(f"{category}\t{amount}")
