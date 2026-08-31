from datetime import datetime
from playwright.sync_api import sync_playwright
from report import get_report_data

def build_html(data: dict) -> str:
    today = datetime.now().strftime("%Y-%m-%d")

    top_products_rows = "".join(
        f"<tr><td>{p['product']}</td><td>${p['revenue']:.2f}</td></tr>"
        for p in data["top_products"]
    )

    import sqlite3
    conn = sqlite3.connect("report.db")
    conn.row_factory = sqlite3.Row
    all_orders = conn.execute(
        "SELECT customer, product, amount, created_at FROM orders ORDER BY created_at DESC"
    ).fetchall()
    conn.close()

    all_orders_rows = "".join(
        f"<tr><td>{o['customer']}</td><td>{o['product']}</td>"
        f"<td>${o['amount']:.2f}</td><td>{o['created_at']}</td></tr>"
        for o in all_orders
    )

    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ margin-bottom: 0; }}
            .subtitle {{ color: #666; margin-top: 4px; }}
            .totals {{ display: flex; gap: 40px; margin: 24px 0; }}
            .total-box {{ border: 1px solid #ccc; padding: 12px 20px; border-radius: 6px; }}
            .total-label {{ font-size: 12px; color: #888; text-transform: uppercase; }}
            .total-value {{ font-size: 24px; font-weight: bold; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
            thead {{ display: table-header-group; }}
            th, td {{ text-align: left; padding: 6px 10px; border-bottom: 1px solid #eee; }}
            th {{ background: #f5f5f5; }}
            tr {{ break-inside: avoid; }}
            h2 {{ margin-top: 40px; }}
        </style>
    </head>
    <body>
        <h1>Sales Report</h1>
        <div class="subtitle">Generated on {today}</div>

        <div class="totals">
            <div class="total-box">
                <div class="total-label">Total Orders</div>
                <div class="total-value">{data['total_orders']}</div>
            </div>
            <div class="total-box">
                <div class="total-label">Total Revenue</div>
                <div class="total-value">${data['total_revenue']:.2f}</div>
            </div>
        </div>

        <h2>Top 5 Products by Revenue</h2>
        <table>
            <thead><tr><th>Product</th><th>Revenue</th></tr></thead>
            <tbody>{top_products_rows}</tbody>
        </table>

        <h2>All Orders</h2>
        <table>
            <thead><tr><th>Customer</th><th>Product</th><th>Amount</th><th>Date</th></tr></thead>
            <tbody>{all_orders_rows}</tbody>
        </table>
    </body>
    </html>
    """
    return html

def render_pdf(html: str, output_path: str):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html)
        page.pdf(path=output_path, format="A4", print_background=True)
        browser.close()

if __name__ == "__main__":
    import os
    os.makedirs("reports", exist_ok=True)
    data = get_report_data()
    html = build_html(data)
    render_pdf(html, "reports/test.pdf")
    print("PDF generated at reports/test.pdf")