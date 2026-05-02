# Requirements Document: Meesho Marketplace Expansion

## Introduction

This document defines production-level requirements for expanding the existing **ShopWave** Flask marketplace into a full Meesho-style platform. It covers all new features, modified flows, access control rules, business logic, and edge cases. It is the authoritative reference for implementation.

**Existing stack**: Flask · SQLAlchemy · SQLite · Bootstrap 5 · Flask-Login  
**Spec type**: Design-first expansion of `shopwave/`

---

## User Roles and Permissions

### Role Definitions

| Role | How Created | Login Method |
|------|-------------|--------------|
| `customer` | Self-register at `/signup` or auto-created on first OTP login | Email+password or mobile OTP |
| `seller` | Self-register at `/signup` selecting "Sell" role | Email+password or mobile OTP |
| `admin` | CLI only (`node scripts/create-admin.js` or Flask CLI) | Email+password only — no OTP |

### Permission Matrix

| Capability | Public | Customer | Seller | Admin |
|---|---|---|---|---|
| View home, about, deals, new arrivals | ✓ | ✓ | ✓ | ✓ |
| Browse products, product detail | ✓ | ✓ | ✓ | ✓ |
| View seller store page | ✓ | ✓ | ✓ | ✓ |
| Subscribe to newsletter | ✓ | ✓ | ✓ | ✓ |
| Register / login | ✓ | — | — | — |
| OTP login | ✓ | — | — | — |
| Add to cart / checkout | — | ✓ | — | — |
| Submit reviews (post-delivery) | — | ✓ | — | — |
| View own orders | — | ✓ | — | — |
| Initiate returns | — | ✓ | — | — |
| Apply referral code | — | ✓ | — | — |
| Create support tickets | — | ✓ | ✓ | — |
| Create / edit / delete own products | — | — | ✓ | — |
| Manage inventory | — | — | ✓ | — |
| Update order status (own items) | — | — | ✓ | — |
| Update shipment tracking | — | — | ✓ | — |
| Respond to return requests | — | — | ✓ | — |
| View seller earnings / wallet | — | — | ✓ | — |
| Request withdrawal | — | — | ✓ | — |
| Submit KYC | — | — | ✓ | — |
| Manage all users | — | — | — | ✓ |
| Approve / reject KYC | — | — | — | ✓ |
| Approve / reject withdrawals | — | — | — | ✓ |
| Manage banners | — | — | — | ✓ |
| Manage coupons | — | — | — | ✓ |
| Handle disputes / returns | — | — | — | ✓ |
| View platform earnings | — | — | — | ✓ |
| View newsletter subscribers | — | — | — | ✓ |
| Delete any product / review | — | — | — | ✓ |

### Role Transition Rules

- A `customer` can become a `seller` by re-registering with the seller role. There is no in-app role upgrade for existing accounts.
- `admin` role is assigned only at account creation via CLI. No API endpoint creates or promotes to admin.
- A deactivated user (`is_active = False`) receives `403 Forbidden` on all authenticated routes.
- Sellers with `kyc_status != 'approved'` can add products but cannot set them to `active` status.

---

## Functional Requirements

### FR-1: Public Pages

**FR-1.1 Home Page (`/`)**
- Displays a Bootstrap 5 Carousel with up to 3 active `Banner` records ordered by `position`.
- If no banners exist, the carousel section is hidden (no broken UI).
- Displays a "Shop by Category" section: distinct categories from active products, shown as pill links.
- Displays a "Deals of the Day" section: up to 8 products where `discount_percent > 20`, ordered by `discount_percent DESC`.
- Displays a "New Arrivals" section: up to 8 products ordered by `created_at DESC`.
- Includes a newsletter subscription form (email input + submit). On submit: `POST /newsletter/subscribe`.
- Includes a floating WhatsApp contact button linking to `https://wa.me/<WHATSAPP_NUMBER>` configured in `config.py`.

**FR-1.2 Product Listing (`/products/`)**
- Displays all active products with `stock > 0` in a responsive grid.
- Each product card shows: primary image, name, price, discount badge (if `discount_percent > 0`), average star rating, "Free Delivery" badge.
- Supports query parameters: `q` (search), `category`, `min_price`, `max_price`, `sort` (`newest`, `price_asc`, `price_desc`, `rating`).
- Paginated: default 20 per page, max 100.
- Category filter pills shown above the grid.

**FR-1.3 Product Detail (`/product/<slug>`)**
- Resolves product by `slug` field. Returns 404 if not found.
- The legacy route `/product/<int:pid>` redirects (301) to the slug URL if the product has a slug.
- Displays: image gallery (up to 5 images from `product.images` comma-separated list), product name, price, MRP with discount percentage, average rating, review count, description, category, seller shop name (linked to `/store/<shop_slug>`).
- If the product has `ProductVariant` records, shows a variant selector (size/color dropdowns). Selecting a variant updates the displayed price via JavaScript.
- "Add to Cart" button: requires login. If variants exist, a variant must be selected before adding.
- "Buy Now" button: adds to cart and immediately redirects to `/checkout`.
- Reviews section: shows all reviews with rating, comment, reviewer name, date. If the current user is a customer who has purchased and received this product, shows a review form.

**FR-1.4 Deals Page (`/deals/`)**
- Lists all active products with `discount_percent > 20` and `stock > 0`.
- Ordered by `discount_percent DESC`.
- Same product card format as `/products/`.

**FR-1.5 New Arrivals (`/new-arrivals/`)**
- Lists the 40 most recently created active products with `stock > 0`.
- Ordered by `created_at DESC`.

**FR-1.6 About Page (`/about/`)**
- Static page. Renders `customer/about.html`.
- Content: platform mission, value proposition, key stats (total sellers, products, orders — queried from DB).

**FR-1.7 Become a Supplier (`/vendors/become-a-supplier/`)**
- Static landing page. Renders `customer/become_supplier.html`.
- Shows platform stats (seller count, product count, order count).
- CTA button links to `/signup` with `?role=seller` pre-selected.

**FR-1.8 Newsletter Subscription (`POST /newsletter/subscribe`)**
- Accepts `email` field from form POST.
- Validates email format. Invalid email returns flash error.
- If email already exists and `is_active=True`: flash "Already subscribed."
- If email exists and `is_active=False`: reactivate, flash "Welcome back!"
- New email: create `Newsletter` record, flash "Subscribed successfully!"
- Redirects back to referring page.

---

### FR-2: Authentication

**FR-2.1 Email/Password Login (`/accounts/login/`)**
- Existing behaviour preserved. Email + password form.
- On success: redirect to role-appropriate dashboard.
- On failure: flash "Invalid credentials."

**FR-2.2 Registration (`/accounts/register/` or `/signup`)**
- Fields: full name, email, phone (optional), password, role selection (Customer / Seller).
- If role = Seller: additional field "Shop Name" (required, unique).
- On seller registration: create `SellerProfile` with `shop_name`, `shop_slug`, `kyc_status='none'`.
- On any registration: generate unique 8-char `referral_code` for the user.
- If `?ref=<code>` query param present: call `referral_service.apply_referral(new_user, code)`.

**FR-2.3 OTP Login (`/accounts/otp/request/`)**
- Step 1 — Request: user enters mobile number (10 digits). System calls `otp_service.generate_otp(mobile)`.
  - Rate limit: max 3 OTP requests per mobile per hour. Exceeding returns flash error and blocks the form.
  - OTP is a 6-digit random integer (100000–999999).
  - OTP stored in `OTPCode` table with `expires_at = now + OTP_EXPIRY_MINUTES` (default 10 min).
  - In development (`DEBUG=True`): OTP printed to console. In production: sent via SMS gateway.
  - Redirect to `/accounts/otp/verify/` with mobile stored in session.
- Step 2 — Verify (`/accounts/otp/verify/`): user enters 6-digit code.
  - Lookup: `OTPCode` where `mobile=mobile`, `code=code`, `is_used=False`, `expires_at > now`.
  - On match: mark `is_used=True`. Find or create `User` with `mobile=mobile`. Call `login_user()`. Redirect to home.
  - On mismatch/expiry: flash "Invalid or expired OTP." Redirect back to verify form.
  - Auto-create user: if no user with that mobile exists, create with `name='User_<last4digits>'`, `role='customer'`, random unusable password hash.

**FR-2.4 Logout (`/accounts/logout/`)**
- Clears session. Redirects to login page.

---

### FR-3: Cart

**FR-3.1 Add to Cart**
- Requires login. Unauthenticated users are redirected to login.
- `POST /cart/add/<pid>` with optional `variant_id` and `quantity`.
- If product has variants and no `variant_id` provided: flash error "Please select a variant."
- If variant is out of stock (`variant.stock = 0`): flash "Out of stock."
- If product has no variants and `product.stock = 0`: flash "Out of stock."
- Quantity cannot exceed available stock. Excess is capped silently.
- If item already in cart: increment quantity (capped at stock).
- Max 50 distinct items in cart. Exceeding returns flash error.

**FR-3.2 Cart Persistence**
- Cart stored in `CartItem` table (not session). Survives logout/login.
- `CartItem` has optional `variant_id` FK. Price at checkout uses `variant.price` if set, else `product.price`.

**FR-3.3 Update / Remove**
- `POST /cart/update/<iid>`: update quantity. If quantity < 1, delete the item.
- `POST /cart/remove/<iid>`: delete item. Flash "Item removed."

---

### FR-4: Orders and Checkout

**FR-4.1 Checkout**
- Requires login. Cart must be non-empty.
- Customer provides delivery address and optional coupon code.
- Coupon validated via `POST /coupon/validate` (AJAX) before order placement.
- On order placement: inventory deducted, cart cleared, `Order` + `OrderItem` + `OrderTimeline` records created, `Shipping` record created with `status='pending'`.
- Payment split: 90% to seller earnings, 10% platform commission (existing logic preserved).
- Order confirmation page shown with `payment_ref`.

**FR-4.2 Order Status Flow**
```
pending → confirmed → shipped → out_for_delivery → delivered → [returned]
                              ↘ cancelled
```
- Customer can cancel only while `status ∈ ['pending', 'confirmed']`.
- Seller updates status for their items.
- Admin can override any status.

**FR-4.3 Shipping Record**
- Created automatically when order is placed (`status='pending'`).
- Seller updates carrier and tracking number via `/seller/shipments/<oid>/update`.
- When `Shipping.status` transitions to `'delivered'`, `Order.status` is automatically updated to `'delivered'` and seller earnings are settled.

---

### FR-5: Returns and Refunds

**FR-5.1 Return Eligibility**
- Customer can initiate a return only if:
  - `order.status = 'delivered'`
  - No existing `Return` record for the same `order_id` with `status != 'rejected'`
  - Return initiated within 7 days of delivery (checked against `Shipping.updated_at` when status became `'delivered'`)

**FR-5.2 Return Flow**
- `POST /orders/<oid>/return` with `reason` field.
- Creates `Return` record with `status='requested'`.
- Seller sees return request at `/seller/returns`.
- Seller can approve or reject via `POST /seller/returns/<rid>/respond`.
- Admin can override at `/admin/disputes`.
- On approval: `Return.status = 'approved'`, `refund_amount` set to `order.total_price`.
- On refund processing: `Return.status = 'refunded'`, customer notified via `Notification`.

**FR-5.3 Partial Returns**
- Not supported in MVP. Returns are per-order (full order return only).
- Future: per-`OrderItem` returns.

---

### FR-6: Reviews and Ratings

**FR-6.1 Eligibility**
- Only customers with `order.status = 'delivered'` for the product may review.
- One review per `(product_id, user_id)` pair (unique constraint).

**FR-6.2 Submission**
- `POST /product/<pid>/review` with `rating` (1–5) and optional `comment`.
- Existing review: update in place.
- Flash "Review submitted!" or "Review updated!"

**FR-6.3 Display**
- Product detail page shows all reviews sorted by `created_at DESC`.
- Average rating computed on read (not stored). Cached in Redis if available.

---

### FR-7: Seller Features

**FR-7.1 Dashboard**
- Shows: product count, total orders, units sold, net earnings (90%), wallet balance, unread notifications count.
- Recent 5 orders table.
- Quick links to all seller sub-pages.

**FR-7.2 Product Management**
- Add product: name, description, price, MRP, stock, category, discount_percent (0–100), up to 5 images, variants (size/color/price/stock).
- Slug auto-generated from name. Uniqueness enforced with `-2`, `-3` suffix.
- Edit product: all fields editable. Slug regenerated only if name changes.
- Delete product: soft-delete not required; hard delete with cascade on variants/cart items.
- Products created with `status='draft'`. Seller can set to `active` only if `kyc_status='approved'`.

**FR-7.3 Inventory Management (`/seller/inventory`)**
- Table showing all products and their variants with current stock levels.
- Inline stock update: `POST /seller/inventory/<pid>/update` with `stock` value.
- Low stock alert: products with `stock < 5` highlighted in amber.

**FR-7.4 Orders Management (`/seller/orders`)**
- Lists all orders containing the seller's products.
- Seller can update status for their items: `confirmed → shipped → out_for_delivery → delivered`.
- Cannot cancel orders (customer-only action).

**FR-7.5 Shipments (`/seller/shipments`)**
- Lists all `Shipping` records for the seller's orders.
- Seller enters carrier name and tracking number.
- `POST /seller/shipments/<oid>/update` updates `Shipping` record.

**FR-7.6 Returns (`/seller/returns`)**
- Lists all `Return` records for the seller's products.
- Seller can approve or reject with a note.
- Approved returns trigger refund notification to customer.

**FR-7.7 Payments & Settlements (`/seller/payments`)**
- Shows `SellerEarnings` records with order reference, gross amount, commission deducted, net amount.
- Shows wallet balance and withdrawal history.
- Withdrawal request form (min ₹100, requires bank details).

**FR-7.8 KYC Submission**
- Seller uploads KYC document (PDF/image, max 5 MB) at `/seller/profile`.
- `kyc_status` transitions: `none → pending` on upload.
- Admin approves/rejects at `/admin/kyc`.

**FR-7.9 Support Tickets (`/seller/support`)**
- Seller creates tickets with subject, description, priority.
- Views own tickets and admin replies.
- Status: `open → in_progress → resolved → closed` (admin-controlled).

**FR-7.10 Notifications (`/seller/notifications`)**
- Lists all `Notification` records for the seller.
- Marks all as read on page load.

---

### FR-8: Admin Features

**FR-8.1 Dashboard**
- Platform stats: total users, sellers, customers, products, orders, gross revenue, platform commission, pending KYC count, pending withdrawal count.
- Revenue chart (last 7 days, Chart.js bar chart).
- Top 5 products by units sold.
- Top 5 sellers by earnings.

**FR-8.2 KYC Management (`/admin/kyc`)**
- Lists all sellers with `kyc_status = 'pending'`.
- Admin can view uploaded KYC document (served via signed URL or direct static path).
- `POST /admin/kyc/<uid>/action` with `action = 'approved' | 'rejected'` and optional `reason`.
- On approval: `kyc_status = 'approved'`, seller notified via `Notification`.
- On rejection: `kyc_status = 'rejected'`, seller notified with reason.
- Rejected seller can resubmit (transitions back to `pending`).

**FR-8.3 Dispute Management (`/admin/disputes`)**
- Lists all `Return` records across all sellers.
- Admin can approve, reject, or mark as refunded.
- `POST /admin/disputes/<rid>/action` with `action`, `refund_amount`, `admin_note`.

**FR-8.4 Banner Management (`/admin/banners`)**
- Lists all banners with image preview, title, link, position, active status.
- `POST /admin/banners/add`: upload image (max 2 MB), set title, link, position.
- `POST /admin/banners/<bid>/delete`: remove banner.
- Toggle active/inactive.
- Max 3 active banners enforced (4th activation deactivates the oldest).

**FR-8.5 Newsletter (`/admin/newsletter`)**
- Lists all `Newsletter` subscribers with email and subscription date.
- Admin can deactivate/reactivate subscribers.
- Export as CSV (optional enhancement).

**FR-8.6 User Management**
- List, filter by role, deactivate/reactivate users.
- Cannot delete admin accounts.

**FR-8.7 Product Moderation**
- Admin can delete any product.
- Admin can set product `status = 'rejected'` with reason.

**FR-8.8 Order Management**
- Admin can view all orders, filter by status.
- Admin can override order status.

---

### FR-9: Referral System

**FR-9.1 Code Generation**
- Every new user gets a unique 8-char alphanumeric `referral_code` on account creation.
- Generated by `referral_service.generate_referral_code()`.

**FR-9.2 Applying a Referral**
- At signup, if `?ref=<code>` is in the URL, the code is applied.
- `referral_service.apply_referral(new_user, code)` creates a `Referral` record with `reward_given=False`.
- Self-referral rejected (referrer_id ≠ referred_id).
- A user can only be referred once (unique constraint on `referred_id`).

**FR-9.3 Reward**
- Reward triggered when referred user places their first order (payment confirmed).
- `referral_service.credit_referral_reward(referral_id)` marks `reward_given=True` and sends a `Notification` to the referrer.
- Reward amount: configurable in `config.py` (`REFERRAL_REWARD = 50`). Credited to referrer's wallet (future: wallet credit; MVP: notification only).

---

### FR-10: Notifications

**FR-10.1 Trigger Events**

| Event | Recipients |
|---|---|
| Order placed | Customer (in-app), Seller (in-app) |
| Order status updated | Customer (in-app) |
| KYC approved/rejected | Seller (in-app) |
| Return approved/rejected | Customer (in-app) |
| Withdrawal approved/rejected | Seller (in-app) |
| Referral reward earned | Referrer (in-app) |

**FR-10.2 Delivery**
- MVP: in-app only (stored in `Notification` table).
- Production: SMS via Twilio, email via SendGrid (async via Bull queue or Celery).

**FR-10.3 Read State**
- Unread count shown in navbar badge.
- Marking as read: page load on `/notifications` marks all as read.

---

## API Endpoint Reference

### Public Endpoints (no auth required)

| Method | URL | Description | Response |
|---|---|---|---|
| GET | `/` | Home page | HTML |
| GET | `/products/` | Product listing with filters | HTML |
| GET | `/product/<slug>` | Product detail | HTML |
| GET | `/deals/` | Deals page | HTML |
| GET | `/new-arrivals/` | New arrivals | HTML |
| GET | `/about/` | About page | HTML |
| GET | `/vendors/become-a-supplier/` | Supplier landing | HTML |
| GET | `/store/<shop_slug>` | Seller storefront | HTML |
| POST | `/newsletter/subscribe` | Subscribe email | Redirect + flash |
| GET/POST | `/accounts/login/` | Email login | HTML / Redirect |
| GET/POST | `/signup` | Register | HTML / Redirect |
| GET/POST | `/accounts/otp/request/` | Request OTP | HTML / Redirect |
| GET/POST | `/accounts/otp/verify/` | Verify OTP | HTML / Redirect |

### Customer Endpoints (login required, role=customer)

| Method | URL | Description |
|---|---|---|
| GET | `/cart` | View cart |
| POST | `/cart/add/<pid>` | Add item (body: `variant_id`, `quantity`) |
| POST | `/cart/update/<iid>` | Update quantity (body: `quantity`) |
| POST | `/cart/remove/<iid>` | Remove item |
| GET | `/checkout` | Checkout page |
| POST | `/checkout` | Place order (body: `address`, `coupon_code`) |
| POST | `/coupon/validate` | Validate coupon (AJAX, body: `code`, `total`) |
| GET | `/orders` | Order history |
| GET | `/orders/<oid>` | Order detail |
| POST | `/orders/<oid>/return` | Initiate return (body: `reason`) |
| POST | `/product/<pid>/review` | Submit review (body: `rating`, `comment`) |
| POST | `/product/<pid>/review/delete` | Delete own review |
| GET | `/notifications` | View notifications |

### Seller Endpoints (login required, role=seller)

| Method | URL | Description |
|---|---|---|
| GET | `/seller/dashboard` | Dashboard overview |
| GET | `/seller/product/add` | Add product form |
| POST | `/seller/product/add` | Create product |
| GET | `/seller/product/<pid>/edit` | Edit product form |
| POST | `/seller/product/<pid>/edit` | Update product |
| POST | `/seller/product/<pid>/delete` | Delete product |
| GET | `/seller/inventory` | Inventory overview |
| POST | `/seller/inventory/<pid>/update` | Update stock (body: `stock`) |
| GET | `/seller/orders` | Orders list |
| POST | `/seller/orders/<oid>/status` | Update order status (body: `status`) |
| GET | `/seller/shipments` | Shipments list |
| POST | `/seller/shipments/<oid>/update` | Update tracking (body: `carrier`, `tracking_number`, `status`) |
| GET | `/seller/returns` | Returns list |
| POST | `/seller/returns/<rid>/respond` | Respond to return (body: `action`, `note`) |
| GET | `/seller/earnings` | Earnings & wallet |
| POST | `/seller/wallet/withdraw` | Request withdrawal (body: `amount`, `upi_id`) |
| GET/POST | `/seller/profile` | Shop profile edit |
| GET | `/seller/support` | Support tickets |
| POST | `/seller/support/new` | Create ticket (body: `subject`, `description`, `priority`) |
| GET | `/seller/notifications` | Notifications |

### Admin Endpoints (login required, role=admin)

| Method | URL | Description |
|---|---|---|
| GET | `/admin` | Dashboard |
| GET | `/admin/users` | User list |
| POST | `/admin/users/<uid>/delete` | Delete user |
| GET | `/admin/sellers` | Seller list |
| GET | `/admin/kyc` | KYC queue |
| POST | `/admin/kyc/<uid>/action` | Approve/reject KYC (body: `action`, `reason`) |
| GET | `/admin/products` | Product list |
| POST | `/admin/products/<pid>/delete` | Delete product |
| GET | `/admin/orders` | Order list |
| POST | `/admin/orders/<oid>/status` | Update order status |
| GET | `/admin/earnings` | Platform earnings |
| GET | `/admin/coupons` | Coupon list |
| POST | `/admin/coupons/add` | Create coupon |
| POST | `/admin/coupons/<cid>/toggle` | Toggle coupon active |
| POST | `/admin/coupons/<cid>/delete` | Delete coupon |
| GET | `/admin/withdrawals` | Withdrawal requests |
| POST | `/admin/withdrawals/<rid>/action` | Approve/reject withdrawal |
| GET | `/admin/reviews` | Review list |
| POST | `/admin/reviews/<rid>/delete` | Delete review |
| GET | `/admin/disputes` | Return/dispute list |
| POST | `/admin/disputes/<rid>/action` | Handle dispute (body: `action`, `refund_amount`, `admin_note`) |
| GET | `/admin/banners` | Banner list |
| POST | `/admin/banners/add` | Add banner (multipart: `image`, `title`, `link`, `position`) |
| POST | `/admin/banners/<bid>/delete` | Delete banner |
| GET | `/admin/newsletter` | Newsletter subscribers |

---

## Business Logic Rules

### OTP Rules
- Max 3 OTP requests per mobile per rolling 1-hour window (counted from `OTPCode.created_at`).
- OTP expires after `OTP_EXPIRY_MINUTES` (default 10) minutes.
- OTP is single-use (`is_used=True` after successful verification).
- OTP is exactly 6 digits (100000–999999).
- Rate limit check uses DB count — no external library required.

### Commission Rules
- Commission rate: 10% platform, 90% seller (configurable in `config.py`).
- Calculated at order placement time (snapshot of rate at that moment).
- `commission + seller_payout = order_item.total_price` must hold exactly.
- Platform commission recorded per order in `PlatformEarnings`.
- Seller earnings settled when `order.status` transitions to `'delivered'`.

### KYC Rules
- Sellers with `kyc_status != 'approved'` cannot set products to `active`.
- KYC document: PDF or image, max 5 MB.
- `kyc_status` transitions: `none → pending → approved | rejected`.
- Rejected sellers can resubmit (transitions back to `pending`).
- Admin must provide a reason when rejecting.

### Return Rules
- Return window: 7 days from delivery date.
- Only one active return per order (cannot request return if one already exists with `status != 'rejected'`).
- Refund amount defaults to `order.total_price` (full order).
- On refund: seller wallet debited by `seller_payout` amount; platform commission not refunded in MVP.

### Referral Rules
- Self-referral rejected.
- A user can only be referred once (unique constraint on `Referral.referred_id`).
- Reward triggered on first completed order only.
- Referral code application window: signup only (cannot apply post-registration).

### Inventory Rules
- Available stock = `product.stock` (or `variant.stock` if variant selected).
- Stock decremented at order placement (not at confirmation).
- If stock reaches 0, product is hidden from storefront automatically.
- Low stock threshold: 5 units (highlighted in seller inventory view).

### Discount Rules
- `discount_percent` range: 0–100 (validated on save).
- Deals page threshold: `discount_percent > 20`.
- Discount badge shown on product card if `discount_percent > 0`.
- MRP must be ≥ price (validated on product save).

### Banner Rules
- Max 3 active banners at any time.
- If admin activates a 4th banner, the banner with the lowest `position` value is deactivated.
- Banner images: max 2 MB, JPEG/PNG/WebP only.

### Coupon Rules
- One coupon per order.
- Coupon `used_count` incremented atomically within the order transaction.
- Expired coupons (`valid_until < now`) return validation error.
- Inactive coupons (`is_active=False`) return validation error.

---

## Edge Cases and Failure Scenarios

### Authentication Edge Cases

| Scenario | Expected Behaviour |
|---|---|
| OTP requested 4th time in 1 hour | Flash "Too many OTP requests. Try again after 1 hour." Block form. |
| OTP submitted after expiry | Flash "Invalid or expired OTP." Redirect to `/accounts/otp/request/`. |
| OTP submitted twice (replay) | Second attempt fails (`is_used=True`). Flash error. |
| Mobile number not registered | Auto-create customer account on first OTP verify. |
| Admin attempts OTP login | OTP login creates a customer account — admin must use email+password. |
| Deactivated user logs in | OTP verified but `403 Forbidden` returned with flash "Account deactivated." |

### Inventory and Order Edge Cases

| Scenario | Expected Behaviour |
|---|---|
| Product goes out of stock between cart add and checkout | Checkout validation re-checks stock. Flash "Item out of stock" for affected items. Customer must remove them. |
| Variant selected but variant is out of stock | `variant.stock = 0` check before add-to-cart. Flash "Selected variant is out of stock." |
| Customer cancels after order is shipped | `422` flash "Cannot cancel a shipped order. Please initiate a return." |
| Return requested after 7-day window | Flash "Return window has expired (7 days from delivery)." |
| Return requested for already-returned order | Flash "A return request already exists for this order." |
| Seller marks delivered but customer disputes | Customer initiates return. Admin handles via `/admin/disputes`. |

### Payment and Wallet Edge Cases

| Scenario | Expected Behaviour |
|---|---|
| Coupon `used_count` hits limit between validate and apply | Atomic increment in order transaction. If limit exceeded, order fails with flash "Coupon no longer valid." |
| Seller wallet balance insufficient for refund debit | Refund still processed. Seller wallet goes negative (flagged for admin review via notification). |
| Withdrawal amount exceeds wallet balance | Flash "Insufficient wallet balance." |
| Duplicate withdrawal request | Max 3 pending withdrawal requests per seller. 4th request blocked with flash error. |

### Seller and KYC Edge Cases

| Scenario | Expected Behaviour |
|---|---|
| Seller tries to activate product before KYC approval | Flash "KYC approval required to publish products." Product stays in `draft`. |
| KYC document upload exceeds 5 MB | Flash "File too large. Maximum 5 MB." |
| Two sellers attempt same shop name | `409` flash "Shop name already taken." |
| Seller account deactivated with active orders | Existing orders continue. Seller cannot log in or create new products. |

### Product and Slug Edge Cases

| Scenario | Expected Behaviour |
|---|---|
| Product name collision on slug generation | Append `-2`, `-3` etc. until unique. |
| Product accessed via old `/product/<int:pid>` URL | 301 redirect to `/product/<slug>` if slug exists. |
| Product has no variants but variant_id posted | Ignore `variant_id`. Use `product.price` and `product.stock`. |
| All product images deleted | Fall back to `product.image` (single image field). |

### Newsletter Edge Cases

| Scenario | Expected Behaviour |
|---|---|
| Invalid email format | Flash "Please enter a valid email address." |
| Already subscribed (active) | Flash "You're already subscribed!" No duplicate record. |
| Previously unsubscribed email | Reactivate `is_active=True`. Flash "Welcome back!" |

---

## Non-Functional Requirements

### Security

| Requirement | Specification |
|---|---|
| Authentication | Flask-Login session-based. Session cookie: HttpOnly, Secure in production. |
| OTP security | 6-digit CSPRNG (`random.randint`); Redis or DB TTL; constant-time comparison; rate-limited. |
| Admin access | CLI-only creation; no admin registration API; `admin_required` decorator on all admin routes. |
| Input validation | All form inputs validated before DB write. Slug sanitised with regex. |
| File uploads | MIME type whitelist; max size enforced; stored in `UPLOAD_FOLDER` outside web root. |
| SQL injection | Prevented by SQLAlchemy ORM parameterised queries. |
| CSRF | Flask-WTF or manual CSRF token on all POST forms (existing pattern preserved). |
| Secrets | All secrets in environment variables; never in source code. |

### Performance

| Requirement | Target |
|---|---|
| Home page load | < 500ms (3 banner images served from CDN or static) |
| Product listing (p95) | < 300ms with pagination |
| OTP delivery (dev) | Instant (console print) |
| OTP delivery (prod) | < 5 seconds via SMS gateway |
| Concurrent users | 1,000 concurrent without degradation (single-server SQLite limit) |

### Scalability

- SQLite is sufficient for MVP (< 100k products, < 10k daily orders).
- Migrate to PostgreSQL when concurrent writes cause lock contention.
- Product search: MySQL FULLTEXT or SQLite FTS5 for text search. Migrate to Elasticsearch at 500k+ products.
- All list endpoints paginated (default 20, max 100).

### Reliability

| Requirement | Specification |
|---|---|
| DB backups | Daily automated SQLite file backup. |
| OTP retry | User can request new OTP after previous expires. |
| Order idempotency | Order placement is transactional; partial failures roll back completely. |
| Graceful 404/403 | Custom error pages rendered via existing error handlers. |

### Observability

- Structured logging via Python `logging` module.
- All errors logged with request context.
- Health check: `GET /health` returns `200 OK { "status": "ok" }`.

---

## Acceptance Criteria Summary

| Feature | Acceptance Criteria |
|---|---|
| Home page | Renders with banners, deals, new arrivals; empty states handled gracefully |
| OTP login | User can log in with mobile; rate limit enforced; auto-account creation works |
| Product slug | All products have unique slugs; old `/product/<id>` URLs redirect correctly |
| Product variants | Variant selector shown when variants exist; cart uses variant price |
| Deals page | Only products with `discount_percent > 20` shown |
| Seller inventory | Stock levels visible; inline update works; low-stock highlighted |
| Shipment tracking | Seller can enter carrier/tracking; customer sees tracking on order detail |
| Returns | Customer can initiate within 7 days; seller/admin can approve/reject |
| KYC workflow | Seller cannot publish products until KYC approved; admin can approve/reject |
| Referral | Code generated on signup; reward triggered on first order |
| Banners | Admin can add/delete banners; max 3 active enforced |
| Newsletter | Email saved; duplicate handled; admin can view subscribers |
| Support tickets | Seller/customer can create; admin can reply and update status |
| Generator fix | Downloading E-commerce project generates working app with all new routes |
