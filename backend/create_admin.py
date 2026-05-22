#!/usr/bin/env python3
"""Create initial admin user. Run after database tables are created.

Usage:
    python create_admin.py --username admin --password admin123 --name 管理员
"""
import argparse
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def main():
    parser = argparse.ArgumentParser(description="Create initial admin user")
    parser.add_argument("--db-url", required=True, help="Database URL, e.g. mysql+pymysql://root:pw@localhost/hotel_manager")
    parser.add_argument("--username", default="admin", help="Admin username")
    parser.add_argument("--password", default="admin123", help="Admin password")
    parser.add_argument("--name", default="管理员", help="Display name")
    args = parser.parse_args()

    engine = create_engine(args.db_url, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        # Check if user already exists
        existing = session.execute(
            text("SELECT id FROM users WHERE username = :username"),
            {"username": args.username},
        ).fetchone()
        if existing:
            print(f"User '{args.username}' already exists (id={existing[0]})")
            return

        hashed = pwd_context.hash(args.password)
        session.execute(
            text("""
                INSERT INTO users (username, password_hash, role, display_name, is_active, created_at, updated_at)
                VALUES (:username, :password_hash, 'admin', :display_name, 1, NOW(), NOW())
            """),
            {"username": args.username, "password_hash": hashed, "display_name": args.name},
        )
        session.commit()
        print(f"Admin user created: username={args.username}, name={args.name}")
        print(f"Login with: {args.username} / {args.password}")


if __name__ == "__main__":
    main()
