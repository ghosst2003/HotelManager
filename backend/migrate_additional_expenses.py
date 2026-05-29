"""
Migrate additional_expenses from JSON column to dedicated table.
"""
import sys
from sqlalchemy import create_engine, text, inspect

if len(sys.argv) < 2:
    print("Usage: python migrate_additional_expenses.py <DATABASE_URL>")
    sys.exit(1)

engine = create_engine(sys.argv[1])

with engine.connect() as conn:
    # Check if migration already done
    inspector = inspect(engine)
    has_json_col = any(
        c["name"] == "additional_expenses"
        for c in inspector.get_columns("order_items")
    )
    has_expenses_table = "additional_expenses" in inspector.get_table_names()

    if has_expenses_table and not has_json_col:
        print("Migration already done.")
        sys.exit(0)

    if not has_json_col:
        print("No additional_expenses column to migrate. Only creating table.")
    else:
        # Create new table first
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS additional_expenses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_item_id INT NOT NULL,
                item VARCHAR(255) NOT NULL DEFAULT '',
                cost DECIMAL(10,2) NOT NULL DEFAULT 0,
                expense DECIMAL(10,2) NOT NULL DEFAULT 0,
                profit DECIMAL(10,2) NOT NULL DEFAULT 0,
                created_at DATETIME NOT NULL DEFAULT NOW(),
                updated_at DATETIME NOT NULL DEFAULT NOW() ON UPDATE NOW(),
                FOREIGN KEY (order_item_id) REFERENCES order_items(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """))

        # Migrate existing JSON data to new table
        rows = conn.execute(text(
            "SELECT id, additional_expenses FROM order_items WHERE additional_expenses IS NOT NULL AND JSON_LENGTH(additional_expenses) > 0"
        )).fetchall()

        for item_id, json_data in rows:
            expenses = json_data  # MySQL returns JSON as list of dicts
            for e in expenses:
                item_name = e.get("item", "")
                cost = float(e.get("cost", 0))
                expense_val = float(e.get("expense", 0))
                profit = expense_val - cost
                conn.execute(text(
                    "INSERT INTO additional_expenses (order_item_id, item, cost, expense, profit) VALUES (:oid, :item, :cost, :exp, :profit)"
                ), {"oid": item_id, "item": item_name, "cost": cost, "exp": expense_val, "profit": profit})

        conn.commit()

        # Drop old JSON column
        conn.execute(text("ALTER TABLE order_items DROP COLUMN additional_expenses"))
        conn.commit()

        print(f"Migrated {len(rows)} order items with additional expenses.")
        print("Migration done: additional_expenses moved to dedicated table.")
