"""
FMCC — Construction Management System
Entry Point — run this file to launch the app.

    python main.py

Build EXE:
    python -m PyInstaller --onefile --windowed --name="FMCC" main.py
"""

from database import create_database
from login import LoginWindow
from gui import Dashboard


def main():
    # 1. Ensure DB + tables exist (seeds admin on first run)
    create_database()

    # 2. Show login window (blocks until closed)
    login = LoginWindow()

    # 3. Open dashboard only if login succeeded
    if login.logged_in_user:
        Dashboard(
            username=login.logged_in_user,
            role=login.logged_in_role
        )


if __name__ == "__main__":
    main()
