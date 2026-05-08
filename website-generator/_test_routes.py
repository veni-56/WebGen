"""Quick route test — run: python _test_routes.py"""
import sys, os
os.environ['SECRET_KEY'] = 'test'
sys.path.insert(0, '.')

import db as database
database.init_db()

from app import create_app
from werkzeug.security import generate_password_hash
import sqlite3

# Create admin test user
try:
    conn = sqlite3.connect(database.DB_PATH)
    conn.execute(
        "INSERT OR IGNORE INTO users (username,email,password_hash,is_admin,plan) VALUES (?,?,?,?,?)",
        ('admin', 'admin@test.com', generate_password_hash('test123'), 1, 'business')
    )
    conn.commit(); conn.close()
except Exception as e:
    print("User create:", e)

a = create_app()
with a.test_client() as c:
    # Login
    r = c.post('/login', data={'username': 'admin', 'password': 'test123'}, follow_redirects=True)
    print(f"Login: {r.status_code}")

    routes = [
        '/dashboard', '/generate', '/wizard/step1',
        '/admin', '/admin/analytics', '/admin/plugins',
        '/admin/notifications', '/notifications', '/pricing',
    ]
    for route in routes:
        resp = c.get(route, follow_redirects=True)
        print(f"{resp.status_code}  {route}")
