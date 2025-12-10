"""
Database reset script for the RAG application
Resets the database to a clean state with default data
"""
import asyncio
import subprocess
import sys
from pathlib import Path

async def reset_database():
    """Reset the database completely"""
    print("🗑️  Resetting database...")

    try:
        # Get the backend directory
        backend_dir = Path(__file__).parent

        # Change to backend directory for running commands
        print("📂 Changing to backend directory...")
        import os
        os.chdir(backend_dir)

        # Downgrade all migrations to base
        print("⬇️  Downgrading migrations...")
        result = subprocess.run(["alembic", "downgrade", "base"],
                              capture_output=True, text=True, cwd=backend_dir)
        if result.returncode != 0:
            print(f"❌ Migration downgrade failed: {result.stderr}")
            return

        # Upgrade migrations to recreate tables
        print("⬆️  Upgrading migrations...")
        result = subprocess.run(["alembic", "upgrade", "head"],
                              capture_output=True, text=True, cwd=backend_dir)
        if result.returncode != 0:
            print(f"❌ Migration upgrade failed: {result.stderr}")
            return

        # Initialize default data
        print("📝 Initializing default data...")
        result = subprocess.run([sys.executable, "init_db.py"],
                              capture_output=True, text=True, cwd=backend_dir)
        if result.returncode != 0:
            print(f"❌ Data initialization failed: {result.stderr}")
            return

        print("✅ Database reset complete!")
        print("\n📋 Default credentials:")
        print("   Email: demo@example.com")
        print("   Password: demo123")
        print("\n🚀 Ready to start the server!")

    except Exception as e:
        print(f"❌ Reset failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(reset_database())