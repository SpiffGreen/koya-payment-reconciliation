#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json
from datetime import datetime
from decimal import Decimal


def parse_amount(value):
    """Amounts arrive as numbers or as strings like "3,218.81"."""
    return Decimal(str(value).replace(",", ""))


def parse_ts(value):
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")


# The file is not in time order, so keep the attempt with the latest timestamp
# for each txn_id rather than the last one seen.
latest = {}

with open("payments.jsonl", encoding="utf-8") as f:
    for line in f:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue  # truncated or blank line
        if not isinstance(event, dict):
            continue

        txn_id = event.get("txn_id")
        if not txn_id:
            continue

        ts = parse_ts(event["ts"])
        if txn_id not in latest or ts > latest[txn_id][0]:
            latest[txn_id] = (ts, event)

total = Decimal(0)
count = 0

for _, event in latest.values():
    if event["status"] == "success":
        total += parse_amount(event["amount"])
        count += 1

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
