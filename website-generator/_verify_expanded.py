import sys, os
sys.path.insert(0, '.')

import generator as g

config = {
    'project_type': 'ecommerce',
    'site_name': 'TestMarket',
    'primary_color': '#e91e63',
    'secondary_color': '#ff5722',
    'font': 'Poppins',
}

try:
    result = g.build_project('test_expanded', config)
    app_py = g.read_file('test_expanded', 'app.py')
    compile(app_py, 'app.py', 'exec')
    print('Syntax: PASS')
except SyntaxError as e:
    print(f'Syntax FAIL: line {e.lineno}: {e.msg}')
    print('Context:', repr(e.text))
    sys.exit(1)
except Exception as e:
    print(f'Build ERROR: {e}')
    import traceback; traceback.print_exc()
    sys.exit(1)

checks = [
    ('deals route',       'def deals()' in app_py),
    ('new_arrivals',      'def new_arrivals()' in app_py),
    ('about route',       'def about()' in app_py),
    ('become_supplier',   'def become_supplier()' in app_py),
    ('otp_request',       'def otp_request()' in app_py),
    ('otp_verify',        'def otp_verify()' in app_py),
    ('seller_inventory',  'def seller_inventory()' in app_py),
    ('seller_shipments',  'def seller_shipments()' in app_py),
    ('seller_returns',    'def seller_returns()' in app_py),
    ('seller_support',    'def seller_support()' in app_py),
    ('admin_kyc',         'def admin_kyc()' in app_py),
    ('admin_disputes',    'def admin_disputes()' in app_py),
    ('admin_banners',     'def admin_banners()' in app_py),
    ('admin_newsletter',  'def admin_newsletter()' in app_py),
    ('banners table',     'CREATE TABLE IF NOT EXISTS banners' in app_py),
    ('otp_codes table',   'CREATE TABLE IF NOT EXISTS otp_codes' in app_py),
    ('shipping table',    'CREATE TABLE IF NOT EXISTS shipping' in app_py),
    ('returns table',     'CREATE TABLE IF NOT EXISTS returns' in app_py),
    ('referrals table',   'CREATE TABLE IF NOT EXISTS referrals' in app_py),
    ('support_tickets',   'CREATE TABLE IF NOT EXISTS support_tickets' in app_py),
    ('newsletter table',  'CREATE TABLE IF NOT EXISTS newsletter' in app_py),
    ('product_variants',  'CREATE TABLE IF NOT EXISTS product_variants' in app_py),
]

all_ok = True
for label, val in checks:
    status = 'PASS' if val else 'FAIL'
    if not val:
        all_ok = False
    print(f'  [{status}] {label}')

print()
print(f'Files generated: {len(result["files"])}')
print('RESULT:', 'ALL PASS' if all_ok else 'SOME FAILED')
