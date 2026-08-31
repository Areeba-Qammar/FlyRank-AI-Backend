import sqlite3
from datetime import datetime, timedelta

DB_PATH = "report.db"

def get_report_data():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

   
    total_orders = cur.execute("SELECT COUNT(*) AS count FROM orders").fetchone()["count"]


    total_revenue = cur.execute("SELECT SUM(amount) AS total FROM orders").fetchone()["total"]

    top_products = cur.execute("""
        SELECT product, SUM(amount) AS revenue
        FROM orders
        GROUP BY product
        ORDER BY revenue DESC
        LIMIT 5
    """).fetchall()
    top_products = [dict(row) for row in top_products]

    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    orders_per_day = cur.execute("""
        SELECT created_at AS date, COUNT(*) AS count
        FROM orders
        WHERE created_at >= ?
        GROUP BY created_at
        ORDER BY created_at
    """, (seven_days_ago,)).fetchall()
    orders_per_day = [dict(row) for row in orders_per_day]

    conn.close()

    return {
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "top_products": top_products,
        "orders_per_day": orders_per_day,
    }

if __name__ == "__main__":
    import json
    print(json.dumps(get_report_data(), indent=2))