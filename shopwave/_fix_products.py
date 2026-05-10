"""Fix: Add missing DB columns + activate all draft products."""
import sqlite3, os

db_path = 'shopwave/shopwave.db'
conn = sqlite3.connect(db_path)

# Add missing columns
for sql in [
    "ALTER TABLE seller_profiles ADD COLUMN kyc_status VARCHAR(20) DEFAULT 'approved'",
    "ALTER TABLE users ADD COLUMN kyc_status VARCHAR(20) DEFAULT 'approved'",
]:
    try:
        conn.execute(sql)
        print(f"Added column: {sql[:50]}")
    except Exception as e:
        print(f"Skip: {e}")

# Set all products active
n = conn.execute("UPDATE products SET status='active' WHERE status='draft'").rowcount
print(f"Activated {n} products")

# Approve all sellers
try:
    n2 = conn.execute("UPDATE seller_profiles SET kyc_status='approved'").rowcount
    print(f"Approved {n2} sellers")
except Exception as e:
    print(f"Seller approve: {e}")

conn.commit()
conn.close()
print("Done! Restart server and check home page.")
