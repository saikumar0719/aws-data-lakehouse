"""Deterministic sample e-commerce data.

Seed 42, so every run produces the same rows. Deliberately includes
the messy cases a real pipeline must handle:
- 5 duplicate order_ids (later updated_at, different amount)
- 1 row with a null amount
- 1 row with a negative amount
- 3 late-arriving rows: earlier order_date, later ingestion_date
"""
import random

import pandas as pd

CUSTOMERS = [f"C{100 + i}" for i in range(10)]
PRODUCTS = [f"P{200 + i}" for i in range(8)]


def generate_orders() -> pd.DataFrame:
    rng = random.Random(42)
    rows = []
    # 100 unique base orders, 2026-10-01 .. 2026-10-10
    for i in range(100):
        day = 1 + (i % 10)
        quantity = rng.randint(1, 4)
        unit_price = round(rng.uniform(10.0, 120.0), 2)
        rows.append(
            {
                "order_id": f"O{1000 + i}",
                "customer_id": CUSTOMERS[i % len(CUSTOMERS)],
                "product_id": PRODUCTS[i % len(PRODUCTS)],
                "order_date": f"2026-10-{day:02d}",
                "ingestion_date": f"2026-10-{day:02d}",
                "updated_at": f"2026-10-{day:02d}T10:00:00",
                "quantity": quantity,
                "unit_price": unit_price,
                "amount": round(quantity * unit_price, 2),
                "status": "completed",
            }
        )
    # 5 duplicates: same order_id, later updated_at, amount + 10
    for j in range(5):
        dup = dict(rows[j])
        dup["updated_at"] = "2026-10-15T09:00:00"
        dup["ingestion_date"] = "2026-10-15"
        dup["amount"] = round(dup["amount"] + 10.0, 2)
        rows.append(dup)
    # 1 null amount
    rows.append(
        {
            "order_id": "O2000",
            "customer_id": "C100",
            "product_id": "P200",
            "order_date": "2026-10-05",
            "ingestion_date": "2026-10-05",
            "updated_at": "2026-10-05T10:00:00",
            "quantity": 1,
            "unit_price": 50.0,
            "amount": None,
            "status": "completed",
        }
    )
    # 1 negative amount
    rows.append(
        {
            "order_id": "O2001",
            "customer_id": "C101",
            "product_id": "P201",
            "order_date": "2026-10-06",
            "ingestion_date": "2026-10-06",
            "updated_at": "2026-10-06T10:00:00",
            "quantity": 1,
            "unit_price": 50.0,
            "amount": -25.0,
            "status": "completed",
        }
    )
    # 3 late-arriving rows: order_date 2026-10-01/02, ingested 2026-10-15
    for k, order_id in enumerate(["O3000", "O3001", "O3002"]):
        rows.append(
            {
                "order_id": order_id,
                "customer_id": CUSTOMERS[k],
                "product_id": PRODUCTS[k],
                "order_date": f"2026-10-0{k + 1}",
                "ingestion_date": "2026-10-15",
                "updated_at": "2026-10-15T08:00:00",
                "quantity": 2,
                "unit_price": 40.0,
                "amount": 80.0,
                "status": "completed",
            }
        )
    return pd.DataFrame(rows)
