import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = "report.db"

PRODUCTS = ["Widget A", "Widget B", "Gadget Pro", "Gizmo Mini", "Thingamajig", "Doohickey"]

def seed():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT NOT NULL,
            product TEXT NOT NULL,
            amount REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    cur.execute("DELETE FROM orders")

    customers = [f"Customer {i}" for i in range(1, 41)]
    now = datetime.now()

    rows = []
    for _ in range(200):
        customer = random.choice(customers)
        product = random.choice(PRODUCTS)
        amount = round(random.uniform(5, 200), 2)
        days_ago = random.randint(0, 29)
        created_at = (now - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        rows.append((customer, product, amount, created_at))

    cur.executemany(
        "INSERT INTO orders (customer, product, amount, created_at) VALUES (?, ?, ?, ?)",
        rows,
    )

    conn.commit()
    conn.close()
    print(f"Seeded {len(rows)} orders into {DB_PATH}")

if __name__ == "__main__":
    seed()