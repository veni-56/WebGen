# Implementation Plan: Meesho Marketplace Expansion

## Overview

Expand the existing `shopwave/` Flask app into a full Meesho-style marketplace by applying all changes described in the design document. The generator has already been patched — this plan covers applying those changes directly to `shopwave/`. Tasks are ordered so each step builds on the previous and nothing is left unintegrated.

## Tasks

- [x] 1. Extend config and shared utilities
  - Add `OTP_EXPIRY_MINUTES = 10`, `OTP_RATE_LIMIT = 3`, `WHATSAPP_NUMBER`, and `REFERRAL_REWARD = 50` to `shopwave/config.py`
  - Create `shopwave/app/utils.py` with a shared `_slugify(text)` helper and `unique_product_slug(name)` function (extracted from `auth/routes.py`, used by seller routes and models)
  - _Requirements: FR-2.3, FR-7.2, FR-1.1, FR-9.3_

- [-] 2. Update database models (`shopwave/app/models.py`)
  - [x] 2.1 Modify `User` model — add `mobile`, `referral_code`, `kyc_status`, `is_active` columns
    - `mobile = db.Column(db.String(15), unique=True, nullable=True)`
    - `referral_code = db.Column(db.String(20), unique=True, nullable=True)`
    - `kyc_status = db.Column(db.String(20), default='none')`
    - `is_active = db.Column(db.Boolean, default=True)`
    - _Requirements: FR-2.3, FR-7.8, FR-9.1, FR-2.2_

  - [x] 2.2 Modify `Product` model — add `slug`, `discount_percent`, `images`, `status` columns and `variants` relationship
    - `slug = db.Column(db.String(220), unique=True, nullable=True)`
    - `discount_percent = db.Column(db.Float, default=0.0)`
    - `images = db.Column(db.Text, default='')`
    - `status = db.Column(db.String(20), default='draft')`
    - Add `variants` relationship to `ProductVariant`
    - _Requirements: FR-1.3, FR-1.4, FR-7.2, FR-7.3_

  - [x] 2.3 Modify `CartItem` model — add optional `variant_id` FK column
    - `variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'), nullable=True)`
    - _Requirements: FR-3.1, FR-3.2_

  - [x] 2.4 Add `ProductVariant` model
    - Fields: `id`, `product_id` (FK), `size`, `color`, `price`, `stock`, `sku`
    - _Requirements: FR-1.3, FR-3.1, FR-7.2_

  - [x] 2.5 Add `OTPCode` model
    - Fields: `id`, `mobile`, `code`, `is_used`, `expires_at`, `created_at`
    - _Requirements: FR-2.3_

  - [x] 2.6 Add `Shipping` model
    - Fields: `id`, `order_id` (FK, unique), `carrier`, `tracking_number`, `status`, `estimated_delivery`, `updated_at`, `created_at`
    - Add `order` relationship with `backref='shipping'` (uselist=False) on `Order`
    - _Requirements: FR-4.3, FR-7.5_

  - [x] 2.7 Add `Return` model
    - Fields: `id`, `order_id` (FK), `customer_id` (FK), `reason`, `status`, `refund_amount`, `admin_note`, `created_at`, `updated_at`
    - _Requirements: FR-5.1, FR-5.2, FR-8.3_

  - [x] 2.8 Add `Referral` model
    - Fields: `id`, `referrer_id` (FK), `referred_id` (FK, unique), `reward_given`, `created_at`
    - Add `referrer` and `referred` relationships with explicit `foreign_keys`
    - _Requirements: FR-9.2, FR-9.3_

  - [x] 2.9 Add `SupportTicket` model
    - Fields: `id`, `user_id` (FK), `subject`, `description`, `status`, `priority`, `admin_reply`, `created_at`, `updated_at`
    - Add `user` relationship with `backref='support_tickets'`
    - _Requirements: FR-7.9_

  - [x] 2.10 Add `Banner` model
    - Fields: `id`, `title`, `image`, `link`, `position`, `is_active`, `created_at`
    - _Requirements: FR-1.1, FR-8.4_

  - [x] 2.11 Add `Newsletter` model
    - Fields: `id`, `email` (unique), `subscribed_at`, `is_active`
    - _Requirements: FR-1.8, FR-8.5_

  - [ ]* 2.12 Write unit tests for new model constraints
    - Test `Referral` unique constraint on `referred_id`
    - Test `Review` unique constraint on `(product_id, user_id)`
    - Test `Coupon.is_valid()` with expired, inactive, and limit-reached states
    - _Requirements: FR-9.2, FR-6.1_

- [-] 3. Implement service layer
  - [x] 3.1 Create `shopwave/app/services/otp_service.py`
    - Implement `can_request_otp(mobile)` — counts `OTPCode` rows in last hour, returns `False` if >= `OTP_RATE_LIMIT`
    - Implement `generate_otp(mobile)` — creates 6-digit code, stores `OTPCode` with `expires_at`, returns code (prints to console in DEBUG)
    - Implement `verify_otp(mobile, code)` — finds valid unused unexpired record, marks `is_used=True`, returns bool
    - _Requirements: FR-2.3_

  - [ ]* 3.2 Write property test for OTP code generation
    - **Property 1: OTP codes are always exactly 6 digits (100000–999999)**
    - **Validates: Requirements FR-2.3**

  - [x] 3.3 Create `shopwave/app/services/shipping_service.py`
    - Implement `create_shipping(order_id)` — inserts `Shipping` record with `status='pending'`
    - Implement `update_tracking(order_id, carrier, tracking_number, status, estimated_delivery=None)` — updates existing `Shipping` record; if status becomes `'delivered'`, also sets `Order.status='delivered'` and settles seller earnings
    - _Requirements: FR-4.3, FR-7.5_

  - [x] 3.4 Create `shopwave/app/services/return_service.py`
    - Implement `request_return(order_id, customer_id, reason)` — validates order is `'delivered'`, no active return exists, within 7-day window; creates `Return` record
    - Implement `process_return(return_id, action, refund_amount, admin_note, actor_id)` — approves/rejects; on approval sets `status='refunded'`, sends `Notification` to customer
    - _Requirements: FR-5.1, FR-5.2_

  - [ ]* 3.5 Write unit tests for return service state machine
    - Test `request_return` raises `ValueError` for non-delivered order
    - Test `request_return` raises `ValueError` when return window expired (> 7 days)
    - Test `request_return` raises `ValueError` when active return already exists
    - _Requirements: FR-5.1_

  - [x] 3.6 Create `shopwave/app/services/referral_service.py`
    - Implement `generate_referral_code(user_id)` — generates unique 8-char alphanumeric code, stores on `User.referral_code`
    - Implement `apply_referral(new_user, referral_code)` — finds referrer, rejects self-referral, creates `Referral` record with `reward_given=False`
    - Implement `credit_referral_reward(referral_id)` — marks `reward_given=True`, sends `Notification` to referrer
    - _Requirements: FR-9.1, FR-9.2, FR-9.3_

  - [ ]* 3.7 Write property test for referral code generation
    - **Property 2: For any user_id, `generate_referral_code` always returns an 8-char alphanumeric string**
    - **Validates: Requirements FR-9.1**

- [ ] 4. Checkpoint — Ensure all tests pass, ask the user if questions arise.

- [-] 5. Update auth blueprint (`shopwave/app/auth/routes.py`)
  - [x] 5.1 Update `signup()` to generate `referral_code` for every new user via `referral_service.generate_referral_code()` and call `referral_service.apply_referral()` if `?ref=<code>` is present
    - Also update redirect after login to use `customer.home` instead of `customer.index`
    - _Requirements: FR-2.2, FR-9.2_

  - [x] 5.2 Add `otp_request()` route — `GET/POST /accounts/otp/request/`
    - On POST: validate 10-digit mobile, call `otp_service.can_request_otp()`, call `otp_service.generate_otp()`, store mobile in session, redirect to verify
    - On rate limit exceeded: flash error and re-render form
    - _Requirements: FR-2.3_

  - [x] 5.3 Add `otp_verify()` route — `GET/POST /accounts/otp/verify/`
    - On POST: read mobile from session, call `otp_service.verify_otp()`, find-or-create `User` with `role='customer'`, call `login_user()`, redirect to home
    - On failure: flash "Invalid or expired OTP." and redirect to request page
    - Check `user.is_active` after login; if False, logout and flash "Account deactivated."
    - _Requirements: FR-2.3_

  - [x] 5.4 Update `login()` to redirect to `customer.home` (not `customer.index`) and check `user.is_active`
    - _Requirements: FR-2.1_

- [-] 6. Update customer blueprint (`shopwave/app/customer/routes.py`)
  - [ ] 6.1 Replace `index()` with `home()` at route `/` — query banners, deals, new arrivals, categories; render `customer/home.html`
    - Keep old `index` name as alias or update all `url_for('customer.index')` references to `customer.home`
    - _Requirements: FR-1.1_

  - [ ] 6.2 Add `product_listing()` at `/products/` — move existing filter/search/sort logic from old `index()` here; add pagination (20 per page); render `customer/products.html`
    - _Requirements: FR-1.2_

  - [ ] 6.3 Add `product_detail_slug()` at `/product/<slug>` — query by slug, load variants and images list, load related products, check user review; render updated `customer/product_detail.html`
    - Update existing `/product/<int:pid>` route to 301-redirect to slug URL if slug exists
    - Update `submit_review` and `delete_review` to also accept slug-based redirect back
    - _Requirements: FR-1.3_

  - [ ] 6.4 Add `deals()` at `/deals/` — filter `discount_percent > 20` and `stock > 0`, order by discount desc; render `customer/deals.html`
    - _Requirements: FR-1.4_

  - [ ] 6.5 Add `new_arrivals()` at `/new-arrivals/` — latest 40 active products by `created_at`; render `customer/new_arrivals.html`
    - _Requirements: FR-1.5_

  - [ ] 6.6 Add `about()` at `/about/` and `become_supplier()` at `/vendors/become-a-supplier/` — query platform stats (user/seller/product/order counts); render respective templates
    - _Requirements: FR-1.6, FR-1.7_

  - [ ] 6.7 Add `newsletter_subscribe()` at `POST /newsletter/subscribe` — validate email, upsert `Newsletter` record, flash appropriate message, redirect to referrer
    - _Requirements: FR-1.8_

  - [ ] 6.8 Add `return_request()` at `POST /orders/<oid>/return` — call `return_service.request_return()`, flash result, redirect to order detail
    - _Requirements: FR-5.1, FR-5.2_

  - [ ] 6.9 Update `add_to_cart()` to handle `variant_id` — validate variant stock, store `variant_id` on `CartItem`, use `variant.price` for total; enforce 50-item cart limit
    - _Requirements: FR-3.1, FR-3.2_

  - [ ] 6.10 Update `checkout()` to use `variant.price` when `cart_item.variant_id` is set; create `Shipping` record via `shipping_service.create_shipping()` after order placement; trigger referral reward on first order
    - _Requirements: FR-4.1, FR-4.3, FR-9.3_

- [ ] 7. Update seller blueprint (`shopwave/app/seller/routes.py`)
  - [ ] 7.1 Update `add_product()` and `edit_product()` to handle `discount_percent`, `images` (up to 5 uploads), `slug` auto-generation via `unique_product_slug()`, and `status` field (block `active` if `kyc_status != 'approved'`)
    - _Requirements: FR-7.2, FR-7.8_

  - [ ] 7.2 Add `inventory()` at `GET /seller/inventory` and `update_inventory()` at `POST /seller/inventory/<pid>/update` — list all seller products+variants with stock; inline stock update
    - _Requirements: FR-7.3_

  - [ ] 7.3 Add `payments()` at `GET /seller/payments` — show `SellerEarnings` with commission breakdown, wallet balance, withdrawal history (extends existing earnings logic)
    - _Requirements: FR-7.7_

  - [ ] 7.4 Add `shipments()` at `GET /seller/shipments` and `update_shipment()` at `POST /seller/shipments/<oid>/update` — list `Shipping` records for seller's orders; call `shipping_service.update_tracking()`
    - _Requirements: FR-7.5_

  - [ ] 7.5 Add `seller_returns()` at `GET /seller/returns` and `respond_return()` at `POST /seller/returns/<rid>/respond` — list `Return` records for seller's products; call `return_service.process_return()` on respond
    - _Requirements: FR-7.6_

  - [ ] 7.6 Add `support_tickets()` at `GET /seller/support` and `create_ticket()` at `POST /seller/support/new` — list and create `SupportTicket` records for current seller
    - _Requirements: FR-7.9_

  - [ ] 7.7 Update `shop_profile()` to handle KYC document upload — save file to `UPLOAD_FOLDER`, set `user.kyc_status = 'pending'`; validate file size (max 5 MB) and type
    - _Requirements: FR-7.8_

- [ ] 8. Update admin blueprint (`shopwave/app/admin/routes.py`)
  - [ ] 8.1 Add `kyc_queue()` at `GET /admin/kyc` and `kyc_action()` at `POST /admin/kyc/<uid>/action` — list sellers with `kyc_status='pending'`; approve/reject with notification to seller
    - _Requirements: FR-8.2_

  - [ ] 8.2 Add `disputes()` at `GET /admin/disputes` and `dispute_action()` at `POST /admin/disputes/<rid>/action` — list all `Return` records; approve/reject/refund with `admin_note`
    - _Requirements: FR-8.3_

  - [ ] 8.3 Add `banners()` at `GET /admin/banners`, `add_banner()` at `POST /admin/banners/add`, and `delete_banner()` at `POST /admin/banners/<bid>/delete`
    - Enforce max 3 active banners: deactivate lowest-position banner when 4th is activated
    - Validate image upload (max 2 MB, JPEG/PNG/WebP)
    - _Requirements: FR-8.4_

  - [ ] 8.4 Add `newsletter()` at `GET /admin/newsletter` — list all `Newsletter` subscribers; allow deactivate/reactivate toggle
    - _Requirements: FR-8.5_

  - [ ] 8.5 Update `dashboard()` to include `pending_kyc` count in stats
    - _Requirements: FR-8.1_

- [ ] 9. Checkpoint — Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Create new templates — auth
  - [ ] 10.1 Create `shopwave/app/templates/auth/otp_request.html`
    - Form: mobile number input (10 digits), submit button, link to email login
    - Show flash messages for rate limit errors
    - Extends `base.html`
    - _Requirements: FR-2.3_

  - [ ] 10.2 Create `shopwave/app/templates/auth/otp_verify.html`
    - Form: 6-digit OTP input, submit button, "Resend OTP" link back to request page
    - Extends `base.html`
    - _Requirements: FR-2.3_

- [ ] 11. Create new templates — customer public pages
  - [ ] 11.1 Create `shopwave/app/templates/customer/home.html`
    - Bootstrap 5 Carousel for banners (hidden if no banners)
    - "Shop by Category" pill links
    - "Deals of the Day" product card grid (up to 8)
    - "New Arrivals" product card grid (up to 8)
    - Newsletter subscription form (POST to `/newsletter/subscribe`)
    - Floating WhatsApp button using `config.WHATSAPP_NUMBER`
    - Extends `base.html`
    - _Requirements: FR-1.1_

  - [ ] 11.2 Create `shopwave/app/templates/customer/products.html`
    - Filter sidebar/pills: category, price range, sort
    - Responsive product card grid with discount badge, rating stars, "Free Delivery" badge
    - Pagination controls
    - Extends `base.html`
    - _Requirements: FR-1.2_

  - [ ] 11.3 Create `shopwave/app/templates/customer/deals.html`
    - Product grid filtered to deals, discount badge prominent
    - Extends `base.html`
    - _Requirements: FR-1.4_

  - [ ] 11.4 Create `shopwave/app/templates/customer/new_arrivals.html`
    - Product grid, "New" badge on cards
    - Extends `base.html`
    - _Requirements: FR-1.5_

  - [ ] 11.5 Create `shopwave/app/templates/customer/about.html`
    - Platform mission, value proposition, key stats (sellers, products, orders from DB)
    - Extends `base.html`
    - _Requirements: FR-1.6_

  - [ ] 11.6 Create `shopwave/app/templates/customer/become_supplier.html`
    - Vendor landing: platform stats, benefits list, CTA button to `/signup?role=seller`
    - Extends `base.html`
    - _Requirements: FR-1.7_

- [ ] 12. Modify existing templates — product detail and base
  - [ ] 12.1 Update `shopwave/app/templates/customer/product_detail.html`
    - Add image gallery (up to 5 images, thumbnail strip + main image)
    - Add variant selector (size/color dropdowns) with JS that updates displayed price on selection
    - Add "Buy Now" button (adds to cart + redirects to checkout)
    - Add return request form/button (shown only if order is delivered and within 7-day window)
    - Update review form to POST to slug-based URL
    - _Requirements: FR-1.3, FR-5.1_

  - [ ] 12.2 Update `shopwave/app/templates/base.html`
    - Add unread notification badge to navbar notification link (query count via template context or context processor)
    - Add "Deals", "New Arrivals", "About", "Become a Supplier" nav links
    - Add floating WhatsApp button (rendered from `WHATSAPP_NUMBER` config)
    - Add OTP login link on login page nav
    - _Requirements: FR-1.1, FR-10.3_

- [ ] 13. Create new templates — seller panel
  - [ ] 13.1 Create `shopwave/app/templates/seller/inventory.html`
    - Table of all products with variant rows, current stock, low-stock highlight (< 5, amber)
    - Inline stock update form per product/variant
    - Extends `base.html`
    - _Requirements: FR-7.3_

  - [ ] 13.2 Create `shopwave/app/templates/seller/payments.html`
    - Earnings table with order ref, gross, commission (10%), net (90%)
    - Wallet balance summary, withdrawal history table
    - Withdrawal request form (amount + UPI ID)
    - Extends `base.html`
    - _Requirements: FR-7.7_

  - [ ] 13.3 Create `shopwave/app/templates/seller/shipments.html`
    - Table of shipments with order ID, customer, carrier, tracking number, status
    - Inline update form per shipment (carrier, tracking, status)
    - Extends `base.html`
    - _Requirements: FR-7.5_

  - [ ] 13.4 Create `shopwave/app/templates/seller/returns.html`
    - Table of return requests with order ID, customer, reason, status
    - Approve/reject form with note field per return
    - Extends `base.html`
    - _Requirements: FR-7.6_

  - [ ] 13.5 Create `shopwave/app/templates/seller/support.html`
    - List of seller's support tickets with status, priority, admin reply
    - New ticket form (subject, description, priority dropdown)
    - Extends `base.html`
    - _Requirements: FR-7.9_

  - [ ] 13.6 Update `shopwave/app/templates/seller/product_form.html`
    - Add `discount_percent` field (0–100), `MRP` field, `status` dropdown
    - Add multi-image upload (up to 5 files)
    - Add variant management section (add/remove size+color+price+stock rows via JS)
    - _Requirements: FR-7.2_

- [ ] 14. Create new templates — admin panel
  - [ ] 14.1 Create `shopwave/app/templates/admin/kyc.html`
    - Table of pending KYC sellers with name, shop, upload date, document link
    - Approve/reject form with reason field per seller
    - Extends `base.html`
    - _Requirements: FR-8.2_

  - [ ] 14.2 Create `shopwave/app/templates/admin/disputes.html`
    - Table of all return/dispute records with order, customer, seller, reason, status
    - Action form per dispute (approve/reject/refund, refund amount, admin note)
    - Extends `base.html`
    - _Requirements: FR-8.3_

  - [ ] 14.3 Create `shopwave/app/templates/admin/banners.html`
    - Banner list with image preview, title, link, position, active toggle
    - Add banner form (image upload, title, link, position)
    - Delete button per banner
    - Extends `base.html`
    - _Requirements: FR-8.4_

  - [ ] 14.4 Create `shopwave/app/templates/admin/newsletter.html`
    - Subscriber table with email, subscribed date, active status
    - Deactivate/reactivate toggle per subscriber
    - Extends `base.html`
    - _Requirements: FR-8.5_

- [ ] 15. Wire up `__init__.py` and run database migration
  - Add a `@app.context_processor` in `shopwave/app/__init__.py` to inject `unread_count` for the navbar badge (queries `Notification` for authenticated users)
  - Ensure `db.create_all()` is called within app context so all new models create their tables (SQLite — no Alembic needed)
  - Import all new models in `models.py` so they are registered with SQLAlchemy metadata
  - _Requirements: FR-10.3_

- [ ] 16. Final checkpoint — Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- All new routes follow the existing decorator pattern: `@login_required` + role decorator
- `db.create_all()` handles new tables automatically via SQLAlchemy — no migration tool needed for SQLite
- The `_slugify` helper moves to `app/utils.py`; `auth/routes.py` and `seller/routes.py` import from there
- Property tests use `hypothesis` library; install with `pip install hypothesis` if not present
