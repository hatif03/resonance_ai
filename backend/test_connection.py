"""Test database connection via IPv6."""
import asyncio
import asyncpg


async def test():
    try:
        conn = await asyncpg.connect(
            host="2406:da1a:6b0:f627:ebcf:2811:f0bb:64f0",
            port=5432,
            user="postgres",
            password="ruyaaihackathon",
            database="postgres",
            timeout=15,
            ssl="require",
        )
        result = await conn.fetchval("SELECT 1")
        print(f"Connection via IPv6 successful! Result: {result}")

        tables = await conn.fetch(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name"
        )
        print(f"Tables: {[t['table_name'] for t in tables]}")
        await conn.close()
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")


asyncio.run(test())
