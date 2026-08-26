import sqlite3
DB_FILE = "tasks.db"
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Create table if it does not exist (Schema uses 'done' column as per spec)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    # Umm Check if table is empty
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    # Seed 3 example tasks ONLY if table is empty
    if count == 0:
        initial_tasks = [
            ("Buy groceries", 0),
            ("Read FastAPI documentation", 1),
            ("Complete Week 3 Database Assignment", 0),
        ]
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)", initial_tasks
        )
        conn.commit()

    conn.close()