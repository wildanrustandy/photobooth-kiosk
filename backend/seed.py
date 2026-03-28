"""
Seed script to create initial admin user and sample booths.
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
from models.booth import Booth
from utils.security import hash_password


# Sample booth configurations
SAMPLE_BOOTHS = [
    {
        "name": "Kiosk Mall Central",
        "location": "Mall Central - Lantai 1, Depan Food Court",
        "config": {
            "price_per_print": 35000,
            "timer_default": 5,
            "max_print": 10,
            "filters": ["Normal", "Grayscale", "Sepia", "Vintage", "Bright"],
            "payment_timeout": 5,
        },
    },
    {
        "name": "Kiosk Mall East",
        "location": "Mall East - Lantai 2, Depan Bioskop",
        "config": {
            "price_per_print": 40000,
            "timer_default": 5,
            "max_print": 10,
            "filters": ["Normal", "Grayscale", "Sepia"],
            "payment_timeout": 5,
        },
    },
    {
        "name": "Kiosk Wedding Venue",
        "location": "Grand Ballroom - Lobby Area",
        "config": {
            "price_per_print": 50000,
            "timer_default": 10,
            "max_print": 15,
            "filters": ["Normal", "Grayscale", "Sepia", "Vintage", "Warm", "Cool"],
            "payment_timeout": 5,
        },
    },
    {
        "name": "Kiosk Cafe Downtown",
        "location": "Jl. Sudirman No. 123 - Cafe Area",
        "config": {
            "price_per_print": 30000,
            "timer_default": 5,
            "max_print": 8,
            "filters": ["Normal", "Grayscale", "Vintage"],
            "payment_timeout": 3,
        },
    },
    {
        "name": "Kiosk Event Center",
        "location": "Convention Center - Hall A Entrance",
        "config": {
            "price_per_print": 45000,
            "timer_default": 5,
            "max_print": 12,
            "filters": ["Normal", "Grayscale", "Sepia", "Vintage", "Bright"],
            "payment_timeout": 5,
        },
    },
]


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


async def create_sample_booths():
    """Create sample booths."""
    async with AsyncSessionLocal() as db:
        created_count = 0

        for booth_data in SAMPLE_BOOTHS:
            # Check if booth already exists
            result = await db.execute(
                select(Booth).where(Booth.name == booth_data["name"])
            )
            existing_booth = result.scalar_one_or_none()

            if existing_booth:
                print(f"Booth '{booth_data['name']}' already exists, skipping...")
                continue

            # Create new booth
            booth = Booth(
                name=booth_data["name"],
                location=booth_data["location"],
                config=booth_data["config"],
                is_active=True,
            )

            db.add(booth)
            created_count += 1
            print(f"✓ Created booth: {booth_data['name']}")

        await db.commit()

        print("=" * 50)
        print(f"Created {created_count} booth(s) successfully!")
        print("=" * 50)

        # List all booths
        result = await db.execute(select(Booth).order_by(Booth.created_at))
        booths = result.scalars().all()

        print("\n📋 Available Booths:")
        print("-" * 50)
        for booth in booths:
            print(f"  • {booth.name}")
            print(f"    Location: {booth.location}")
            print(f"    Price: Rp {booth.config.get('price_per_print', 0):,}")
            print(f"    Status: {'Active' if booth.is_active else 'Inactive'}")
            print()


async def main():
    """Main function."""
    print("Initializing database...")
    await init_db()
    print("Database initialized.")

    print("\nCreating admin user...")
    await create_admin_user()

    print("\nCreating sample booths...")
    await create_sample_booths()

    print("\n✅ Seed completed!")


if __name__ == "__main__":
    asyncio.run(main())
