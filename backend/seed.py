"""
Seed script to create initial admin user.
Run this script after database initialization.

Usage:
    python seed.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select
from database import AsyncSessionLocal, init_db
from models.admin_user import AdminUser
from utils.security import hash_password


async def create_admin_user():
    """Create initial admin user."""
    async with AsyncSessionLocal() as db:
        # Check if admin already exists
        result = await db.execute(
            select(AdminUser).where(AdminUser.username == "admin")
        )
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            print("Admin user already exists!")
            print(f"Username: {existing_admin.username}")
            print(f"Role: {existing_admin.role}")
            return

        # Create new admin user
        admin = AdminUser(
            username="admin",
            password_hash=hash_password("admin123"),  # Change this in production!
            role="super_admin",
            is_active=True,
        )

        db.add(admin)
        await db.commit()
        await db.refresh(admin)

        print("=" * 50)
        print("Admin user created successfully!")
        print("=" * 50)
        print("Username: admin")
        print("Password: admin123")
        print("Role: super_admin")
        print("=" * 50)
        print("⚠️  IMPORTANT: Change the password in production!")
        print("=" * 50)


async def main():
    """Main function."""
    print("Initializing database...")
    await init_db()
    print("Database initialized.")

    print("\nCreating admin user...")
    await create_admin_user()


if __name__ == "__main__":
    asyncio.run(main())
