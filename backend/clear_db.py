"""Script to clear all data from the database."""

import asyncio

from sqlalchemy import text

from database import async_engine


async def clear_all():
    """Truncate all tables to clear data while keeping structure."""
    async with async_engine.begin() as conn:
        print("Clearing all tables...")
        await conn.execute(
            text(
                "TRUNCATE TABLE photos, payments, sessions, device_sessions, booths, admin_users CASCADE"
            )
        )
        print("All tables cleared successfully!")


if __name__ == "__main__":
    asyncio.run(clear_all())
