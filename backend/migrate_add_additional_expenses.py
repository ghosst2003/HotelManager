"""Add additional_expenses JSON column to order_items table."""
import sys
from sqlalchemy import create_engine, text

if len(sys.argv) < 2:
    print("Usage: python migrate_add_additional_expenses.py <DATABASE_URL>")
    sys.exit(1)

engine = create_engine(sys.argv[1])

with engine.connect() as conn:
    conn.execute(text(
        "ALTER TABLE order_items ADD COLUMN additional_expenses JSON DEFAULT NULL"
    ))
    conn.commit()

print("Migration done: added 'additional_expenses' column to order_items table")
