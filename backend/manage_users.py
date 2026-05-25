#!/usr/bin/env python3
"""User management script: add users, reset passwords.

Usage:
    # Add a user
    python manage_users.py add --db-url "mysql+pymysql://root:pw@localhost/hotel_manager" --username zhangsan --password abc123 --name 张三 --role employee

    # Reset a user's password
    python manage_users.py reset --db-url "mysql+pymysql://root:pw@localhost/hotel_manager" --username zhangsan --password newpass

    # List all users
    python manage_users.py list --db-url "mysql+pymysql://root:pw@localhost/hotel_manager"

    # Disable/enable a user
    python manage_users.py disable --db-url "mysql+pymysql://root:pw@localhost/hotel_manager" --username zhangsan
    python manage_users.py enable --db-url "mysql+pymysql://root:pw@localhost/hotel_manager" --username zhangsan
"""
import argparse
import sys
from sqlalchemy import create_engine, text
import bcrypt


def get_db_session(db_url):
    engine = create_engine(db_url, pool_pre_ping=True)
    from sqlalchemy.orm import sessionmaker
    return sessionmaker(bind=engine)()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")


def cmd_add(args):
    session = get_db_session(args.db_url)
    existing = session.execute(text("SELECT id FROM users WHERE username = :username"), {"username": args.username}).fetchone()
    if existing:
        print(f"Error: user '{args.username}' already exists (id={existing[0]})")
        sys.exit(1)

    hashed = hash_password(args.password)
    session.execute(
        text("""
            INSERT INTO users (username, password_hash, role, display_name, is_active, created_at, updated_at)
            VALUES (:username, :password_hash, :role, :display_name, 1, NOW(), NOW())
        """),
        {"username": args.username, "password_hash": hashed, "role": args.role, "display_name": args.name},
    )
    session.commit()
    print(f"User created: username={args.username}, name={args.name}, role={args.role}")
    print(f"Login with: {args.username} / {args.password}")


def cmd_reset(args):
    session = get_db_session(args.db_url)
    existing = session.execute(text("SELECT id, display_name FROM users WHERE username = :username"), {"username": args.username}).fetchone()
    if not existing:
        print(f"Error: user '{args.username}' not found")
        sys.exit(1)

    hashed = hash_password(args.password)
    session.execute(
        text("UPDATE users SET password_hash = :hash, updated_at = NOW() WHERE username = :username"),
        {"hash": hashed, "username": args.username},
    )
    session.commit()
    print(f"Password reset for {existing[1]} ({args.username})")
    print(f"Login with: {args.username} / {args.password}")


def cmd_list(args):
    session = get_db_session(args.db_url)
    rows = session.execute(text("SELECT id, username, display_name, role, is_active, created_at FROM users ORDER BY id")).fetchall()
    if not rows:
        print("No users found.")
        return
    print(f"{'ID':<4} {'Username':<15} {'Name':<12} {'Role':<10} {'Active':<6} {'Created'}")
    print("-" * 70)
    for r in rows:
        print(f"{r[0]:<4} {r[1]:<15} {r[2]:<12} {r[3]:<10} {'Yes' if r[4] else 'No':<6} {r[5]}")


def cmd_toggle(args):
    session = get_db_session(args.db_url)
    action = 1 if args.action == "enable" else 0
    existing = session.execute(text("SELECT id, display_name FROM users WHERE username = :username"), {"username": args.username}).fetchone()
    if not existing:
        print(f"Error: user '{args.username}' not found")
        sys.exit(1)

    session.execute(
        text("UPDATE users SET is_active = :active, updated_at = NOW() WHERE username = :username"),
        {"active": action, "username": args.username},
    )
    session.commit()
    print(f"User {existing[1]} ({args.username}) {'enabled' if action else 'disabled'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hotel system user management")
    sub = parser.add_subparsers(dest="command")

    p_add = sub.add_parser("add", help="Add a new user")
    p_add.add_argument("--db-url", required=True)
    p_add.add_argument("--username", required=True)
    p_add.add_argument("--password", required=True)
    p_add.add_argument("--name", required=True)
    p_add.add_argument("--role", choices=["employee", "finance", "admin"], required=True)
    p_add.set_defaults(func=cmd_add)

    p_reset = sub.add_parser("reset", help="Reset a user's password")
    p_reset.add_argument("--db-url", required=True)
    p_reset.add_argument("--username", required=True)
    p_reset.add_argument("--password", required=True)
    p_reset.set_defaults(func=cmd_reset)

    p_list = sub.add_parser("list", help="List all users")
    p_list.add_argument("--db-url", required=True)
    p_list.set_defaults(func=cmd_list)

    p_toggle = sub.add_parser("toggle", help="Enable/disable a user")
    p_toggle.add_argument("--db-url", required=True)
    p_toggle.add_argument("--username", required=True)
    p_toggle.add_argument("action", choices=["enable", "disable"])
    p_toggle.set_defaults(func=cmd_toggle)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)
