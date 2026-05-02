# Marketplace Generator Upgrade

The e-commerce generator now outputs a **full multi-vendor marketplace** (Meesho-style) with:

- 3 roles: Admin / Seller / Customer
- Payment split: 90% seller, 10% platform commission
- Full Blueprint architecture
- Earnings tracking in database

## What Changed

`generator.py` → `_gen_ecommerce()` now generates:
- Single-file `app.py` with all routes (session-based auth)
- 7 database tables (users, products, cart_items, orders, order_items, seller_earnings, platform_earnings)
- 20+ templates (auth, customer, seller, admin)
- Payment split logic on checkout

## Reference Implementation

The working reference is in `../shopwave/` — all templates and logic are production-tested.

## To Apply

The `_mv_app_py()` function in `generator.py` (line 594) needs the correct marketplace code.
The patch script `_patch_generator.py` has the correct NEW_BODY but has syntax issues.

## Manual Fix

Replace lines 594-872 in `generator.py` with the correct `_mv_app_py` implementation from `_patch_generator.py` NEW_BODY (lines 18-228), fixing the triple-quote escaping.

Then add all missing `_mv_*` template helper functions before `_ecom_base_html` (line 874).
