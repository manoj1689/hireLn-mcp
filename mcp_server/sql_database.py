import aiosqlite
import asyncio

class Database:
    """Async SQLite database wrapper."""

    def __init__(self, db_path: str = "app.db"):
        self.db_path = db_path
        self.conn = None

    @classmethod
    async def connect(cls, db_path: str = "app.db"):
        self = cls(db_path)
        self.conn = await aiosqlite.connect(db_path)
        self.conn.row_factory = aiosqlite.Row
        return self

    async def disconnect(self):
        if self.conn:
            await self.conn.close()

    async def execute(self, sql: str, params: tuple = ()):
        async with self.conn.execute(sql, params) as cursor:
            await self.conn.commit()
            return cursor.lastrowid

    async def query(self, sql: str, params: tuple = ()):
        async with self.conn.execute(sql, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def main():
    db = await Database.connect()

    # Create table if not exists
    await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    """)

    # Insert user from terminal
    name = input("Enter name: ")
    email = input("Enter email: ")

    try:
        user_id = await db.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (name, email)
        )
        print(f"✅ User added with ID {user_id}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Show all users
    users = await db.query("SELECT * FROM users")
    print("\n📋 All Users:")
    for u in users:
        print(f"ID: {u['id']}, Name: {u['name']}, Email: {u['email']}")

    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
