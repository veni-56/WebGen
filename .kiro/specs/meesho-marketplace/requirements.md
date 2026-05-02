# Requirements Document: Meesho Marketplace

## Introduction

This document defines the functional and non-functional requirements for a production-grade multi-vendor ecommerce marketplace platform modelled after Meesho. It is intended for engineering teams implementing the system described in `design.md`.

**Tech Stack**: Node.js + Express · MySQL + Sequelize · React + Tailwind · JWT + OTP · Redis · Bull · AWS S3 / Cloudinary

---

## User Roles and Permissions

### Role Matrix

| Capability | Customer | Seller | Admin |
|---|---|---|---|
| Register / login via OTP | ✓ | ✓ | — |
| Admin created via CLI only | — | — | ✓ |
| Browse products | ✓ | ✓ | ✓ |
| Add to cart / checkout | ✓ | — | — |
| Submit reviews (post-delivery) | ✓ | — | — |
| Create / edit own products | — | ✓ | — |
| Submit KYC + bank details | — | ✓ | — |
| Update order status (own items) | — | ✓ | — |
| Request wallet withdrawal | — | ✓ | — |
| Approve / reject KYC | — | — | ✓ |
| Approve / reject withdrawals | — | — | ✓ |
| Manage all users, products, orders | — | — | ✓ |
| Create / manage coupons | — | — | ✓ |
| View platform earnings | — | — | ✓ |
| Set per-seller commission rate | — | — | ✓ |
| Manage support tickets | — | — | ✓ |

### Role Transition Rules

- A `customer` account can self-upgrade to `seller` by calling `POST /sellers/onboard`. The role field on `users` is updated to `seller` and a `seller_profiles` row is created.
- A `seller` cannot downgrade back to `customer` via API.
- `admin` role is assigned only at account creation time via the CLI script `node scripts/create-admin.js`. There is no API endpoint that creates or promotes to admin.
- A deactivated user (`is_active = false`) receives `403 Forbidden` on all authenticated endpoints.

---

## Functional Requirements

### FR-1: Authentication System

**FR-1.1 OTP Request**
- The system MUST accept either a 10-digit phone number or a valid email address as the identifier.
- The system MUST generate a cryptographically random 6-digit OTP.
- The OTP MUST be stored in Redis with a 5-minute TTL keyed as `otp:<identifier>`.
- The system MUST enqueue an async delivery job (Bull) to send the OTP via Twilio (SMS) or SendGrid (email) based on the `channel` field.
- The system MUST enforce a rate limit of 3 OTP requests per identifier per hour. Exceeding this returns `429 Too Many Requests`.
- The response MUST NOT include the OTP value.

**FR-1.2 OTP Verification**
- The system MUST compare the submitted OTP against the Redis-stored value in constant time to prevent timing attacks.
- On match: delete the Redis key, find-or-create the user record, issue a JWT access token (15-min expiry) and refresh token (7-day expiry).
- On mismatch or expiry: return `401 Unauthorized { "error": "Invalid or expired OTP" }`.
- The refresh token MUST be stored in an httpOnly, Secure, SameSite=Strict cookie.
- The access token MUST be returned in the response body.

**FR-1.3 Token Refresh**
- `POST /auth/refresh` accepts the refresh token from the httpOnly cookie.
- Returns a new access token. Does not rotate the refresh token unless it is within 24 hours of expiry.

**FR-1.4 Logout**
- `POST /auth/logout` invalidates the refresh token by adding it to a Redis blocklist with TTL equal to its remaining lifetime.

**FR-1.5 Admin Account Creation**
- Admin accounts MUST only be created via `node scripts/create-admin.js`.
- The script MUST prompt for email and password interactively (not as CLI args) to avoid shell history exposure.
- The password MUST be hashed with bcrypt (cost factor ≥ 12) before storage.
- Admin login uses `POST /auth/admin-login` with email + password (not OTP).

---

### FR-2: User Management

**FR-2.1 Profile**
- `GET /users/me` returns the authenticated user's profile including role, referral code, and wallet balance.
- `PUT /users/me` allows updating name, profile picture URL, and default shipping address. Email and phone cannot be changed via this endpoint.

**FR-2.2 Admin User Management**
- `GET /users` supports filtering by `role`, `is_active`, and date range. Paginated (default 20, max 100).
- `PATCH /users/:id/status` toggles `is_active`. Deactivating a user with active orders does not cancel those orders but prevents new logins.

---

### FR-3: Seller Onboarding

**FR-3.1 Registration**
- A customer calls `POST /sellers/onboard` with `shop_name` (required, unique) and optional `description`.
- The system creates a `seller_profiles` row with `kyc_status = 'pending'` and updates `users.role = 'seller'`.
- A wallet row is created for the seller at this point with `balance = 0`.

**FR-3.2 KYC Submission**
- `PUT /sellers/kyc` accepts `pan_number`, `gst_number` (optional), and a `kyc_doc` file upload (PDF or image, max 5 MB).
- The document is uploaded to a private S3 bucket. The URL is stored in `seller_profiles.kyc_doc_url`.
- `kyc_status` transitions to `'submitted'`.
- A seller with `kyc_status != 'approved'` CANNOT publish products (products remain in `draft` status).

**FR-3.3 KYC Review (Admin)**
- `PATCH /sellers/:id/kyc` with `{ "status": "approved" | "rejected", "reason": "..." }`.
- On approval: `kyc_status = 'approved'`; seller is notified via in-app notification + email.
- On rejection: `kyc_status = 'rejected'`; rejection reason stored; seller notified with reason.
- A rejected seller may resubmit KYC (transitions back to `'submitted'`).

**FR-3.4 Bank Details**
- `PUT /sellers/bank` accepts `bank_account`, `bank_ifsc`, `bank_name`.
- Bank details are required before a withdrawal request can be submitted.
- Bank details are stored encrypted at rest (AES-256).

**FR-3.5 Commission Rate**
- Default commission rate is 10% (configurable via `PATCH /admin/config/commission`).
- Admin can set a per-seller override via `PATCH /sellers/:id/commission { "rate": 8.5 }`.
- Rate must be between 0 and 50 (inclusive).

---

### FR-4: Product Catalog

**FR-4.1 Product Creation**
- Only sellers with `kyc_status = 'approved'` may create products.
- Required fields: `category_id`, `name`, `base_price`, `mrp`, at least one variant.
- `mrp` MUST be ≥ `base_price`. Violation returns `422 Unprocessable Entity`.
- New products are created with `status = 'draft'` and are not visible to customers until approved.
- A product MUST have at least one active variant with `inventory.quantity ≥ 0`.

**FR-4.2 Product Variants**
- Each variant has a unique `sku` (system-generated if not provided: `<product_id>-<color>-<size>`).
- Variant attributes: `size`, `color`, `material` (all optional individually, but at least one must differ from sibling variants).
- Each variant has its own `price` (may differ from `base_price`) and its own inventory row.
- Deactivating a variant (`is_active = false`) removes it from the storefront but preserves historical order data.

**FR-4.3 Product Approval (Admin)**
- `PATCH /products/:id/status { "status": "active" | "rejected", "reason": "..." }`.
- Only admin can transition `draft → active` or `draft → rejected`.
- A seller can transition `active → inactive` (temporarily hide) and `inactive → active` without re-approval.
- Rejected products require re-submission (seller edits and resubmits; status returns to `draft`).

**FR-4.4 Product Search**
- `GET /products` supports full-text search (`q`), category filter, price range (`min_price`, `max_price`), and sort (`price_asc`, `price_desc`, `newest`, `rating`).
- Results are paginated. Only `status = 'active'` products with at least one variant having `inventory.quantity - inventory.reserved > 0` are returned.
- Product listings are cached in Redis with a 5-minute TTL. Cache is invalidated on product update or inventory change.

**FR-4.5 Image Upload**
- `POST /products/:id/images` accepts up to 8 images per product (multipart/form-data).
- Accepted MIME types: `image/jpeg`, `image/png`, `image/webp`. Max 5 MB per file.
- Images are uploaded to S3/Cloudinary and URLs stored in `products.images` (JSON array).
- The first image in the array is treated as the primary display image.

---

### FR-5: Cart

**FR-5.1 Add to Cart**
- `POST /cart { "variant_id": "uuid", "quantity": 2 }`.
- If the variant is already in the cart, quantity is incremented (not replaced).
- Quantity cannot exceed `inventory.quantity - inventory.reserved`.
- Adding an out-of-stock variant returns `409 Conflict`.

**FR-5.2 Cart Persistence**
- Cart is persisted in the `cart` table (not session/cookie). It survives logout and re-login.
- A user may have at most 50 distinct items in their cart. Exceeding this returns `422`.

**FR-5.3 Cart Validation at Checkout**
- Before order placement, the system re-validates each cart item's availability. Items that have become unavailable are flagged in the response and must be removed before proceeding.

---

### FR-6: Order Management

**FR-6.1 Order Placement**
- Customer provides `shipping_address`, optional `coupon_code`, and `payment_method`.
- The system executes the following atomically in a single DB transaction:
  1. Validate all cart items have sufficient available inventory (`quantity - reserved ≥ cart.quantity`).
  2. Reserve inventory (`reserved += cart.quantity`) using row-level locks.
  3. Apply coupon discount if provided.
  4. Create `orders` row with `status = 'pending'`.
  5. Create `order_items` rows with pre-calculated `commission` and `seller_payout`.
  6. Create `payments` row with `status = 'pending'`.
  7. Clear the cart.
- If any step fails, the entire transaction is rolled back and inventory is not reserved.

**FR-6.2 Order Status Flow**

```
pending → confirmed → processing → shipped → delivered
                                           ↘ cancelled
                                           ↘ returned
```

- `pending → confirmed`: triggered by successful payment confirmation.
- `confirmed → processing`: seller acknowledges the order.
- `processing → shipped`: seller provides tracking number.
- `shipped → delivered`: seller marks delivered OR shipping carrier webhook.
- Any status → `cancelled`: allowed by customer before `shipped`; by admin at any time.
- `delivered → returned`: customer initiates return within the return window (7 days).

**FR-6.3 Inventory Deduction**
- Inventory is deducted (`quantity -= reserved`, `reserved -= reserved`) only when `status` transitions to `confirmed`.
- If an order is cancelled before confirmation, the reservation is released (`reserved -= cart.quantity`).

**FR-6.4 Order Visibility**
- Customers see only their own orders.
- Sellers see only orders containing their products (via `order_items.seller_id`).
- Admins see all orders.

**FR-6.5 Cancellation Rules**
- Customer can cancel an order only while `status ∈ ['pending', 'confirmed', 'processing']`.
- Cancellation after `shipped` is not allowed via API; customer must initiate a return instead.
- On cancellation: inventory reservation released; payment refunded if already captured.

---

### FR-7: Payments

**FR-7.1 Payment Confirmation**
- `POST /payments/confirm { "order_id": "uuid", "gateway_ref": "..." }` is called by the frontend after the payment gateway redirects back.
- The system verifies the payment status with the gateway (server-to-server call).
- On success: `payments.status = 'completed'`; order status transitions to `confirmed`; commission settlement is enqueued.
- On failure: `payments.status = 'failed'`; order remains `pending`; inventory reservation is released after 30 minutes if not retried.

**FR-7.2 Webhook**
- `POST /payments/webhook` is a public endpoint that accepts gateway callbacks.
- The request MUST include a valid HMAC-SHA256 signature in the `X-Gateway-Signature` header. Invalid signatures return `401`.
- The endpoint is idempotent: duplicate webhooks for the same `gateway_ref` are silently ignored.
- A reconciliation Bull job runs every 15 minutes to catch orders stuck in `pending` with a completed payment.

**FR-7.3 Refunds**
- Refunds are triggered by order cancellation (if payment was captured) or return approval.
- Refund amount is credited to the customer's wallet or original payment method depending on the `refund_method` field.
- `payments.status` transitions to `'refunded'`.

---

### FR-8: Wallet and Commission

**FR-8.1 Commission Calculation**
- For each `order_item`, commission is calculated at order placement time (not at settlement) and stored in `order_items.commission` and `order_items.seller_payout`.
- Formula: `commission = total_price × (commission_rate / 100)`, `seller_payout = total_price - commission`.
- The commission rate used is the seller's current rate at the time of order placement (snapshot, not live).

**FR-8.2 Earnings Settlement**
- Earnings are settled when an `order_item` transitions to `delivered`.
- Settlement creates a `seller_earnings` row with `status = 'settled'` and credits `wallets.balance` for the seller.
- A `platform_earnings` row is created simultaneously in the same transaction.
- If settlement fails (e.g., DB error), it is retried via the `commission.worker.js` Bull job with exponential backoff.

**FR-8.3 Withdrawal Requests**
- `POST /wallet/withdraw { "amount": 500, "bank_account": "..." }`.
- Preconditions: seller has `kyc_status = 'approved'`, bank details on file, `wallet.balance ≥ amount`, `amount ≥ 100` (minimum withdrawal).
- Creates a `withdrawal_requests` row (not a separate table — tracked via a status field on `wallets` or a dedicated table per design).
- Admin approves via `PATCH /wallet/withdrawals/:id { "status": "approved" | "rejected" }`.
- On approval: `wallet.balance -= amount`; payout initiated via bank transfer API.
- On rejection: balance unchanged; seller notified with reason.

**FR-8.4 Wallet Balance Integrity**
- All wallet debits and credits MUST occur inside DB transactions.
- `wallet.balance` MUST never go negative. Any operation that would result in a negative balance returns `422`.

---

### FR-9: Shipping and Tracking

**FR-9.1 Shipping Record Creation**
- A `shipping` row is created when an order transitions to `processing`.
- Seller provides `carrier` and `tracking_number` when transitioning to `shipped`.

**FR-9.2 Tracking Updates**
- `PUT /shipping/:orderId { "status": "in_transit", "tracking_number": "..." }`.
- Status flow: `pending → picked_up → in_transit → out_for_delivery → delivered | failed`.
- When `shipping.status = 'delivered'`, the `order.status` is automatically updated to `delivered` and earnings settlement is triggered.

---

### FR-10: Returns and Refunds

**FR-10.1 Return Eligibility**
- A customer may initiate a return only if:
  - `order_item.status = 'delivered'`
  - The return is initiated within 7 days of delivery (`shipping.delivered_at`).
  - No existing return request exists for the same `order_item_id`.

**FR-10.2 Return Flow**
- `POST /returns { "order_item_id": "uuid", "reason": "...", "images": [...] }`.
- Status flow: `requested → approved | rejected → picked_up → refunded`.
- Seller or admin approves/rejects via `PATCH /returns/:id/status`.
- On approval: a reverse pickup is scheduled; `order_item.status` transitions to `returned`.
- On refund completion: `payments` row updated to `refunded`; customer wallet credited.

**FR-10.3 Refund Amount**
- Refund amount = `order_item.total_price` (full item price, not including shipping charge unless all items are returned).
- If the seller's earnings were already settled, the settled amount is debited from the seller's wallet.

---

### FR-11: Reviews and Ratings

**FR-11.1 Review Eligibility**
- A customer may submit exactly one review per `(product_id, order_id)` pair.
- Reviews can only be submitted after `order_item.status = 'delivered'`.
- Attempting to review before delivery returns `403 Forbidden`.

**FR-11.2 Review Content**
- Required: `rating` (integer 1–5).
- Optional: `title` (max 100 chars), `body` (max 1000 chars), up to 3 images.
- Reviews are marked `is_verified = true` automatically (since they require a confirmed purchase).

**FR-11.3 Product Rating Aggregation**
- The product's average rating is computed on read (not stored) from the `reviews` table.
- Cached in Redis with a 10-minute TTL per product.

**FR-11.4 Admin Moderation**
- `DELETE /reviews/:id` (admin only) removes a review. Soft-delete preferred (add `deleted_at` column).

---

### FR-12: Coupons

**FR-12.1 Coupon Creation (Admin)**
- Fields: `code` (unique, uppercase), `type` (`percentage` | `flat`), `value`, `min_order_value`, `max_discount` (for percentage type), `usage_limit`, `valid_from`, `valid_until`.
- `value` for percentage type must be between 1 and 100.
- `value` for flat type must be > 0 and < `min_order_value`.

**FR-12.2 Coupon Validation**
- `POST /coupons/validate { "code": "SAVE50", "cart_total": 999 }`.
- Returns the computed discount amount and the final total.
- Validation checks: coupon exists, `is_active = true`, current time within `valid_from`–`valid_until`, `used_count < usage_limit` (if set), `cart_total ≥ min_order_value`.

**FR-12.3 Coupon Application**
- A coupon is applied at order placement. `used_count` is incremented atomically within the order transaction.
- Only one coupon may be applied per order.
- The coupon ID is stored on the `orders` row for audit purposes.

---

### FR-13: Notifications

**FR-13.1 In-App Notifications**
- Every significant event creates a `notifications` row for the relevant user(s).
- Events that trigger notifications:

| Event | Recipients |
|---|---|
| OTP requested | User (via SMS/email only, no in-app) |
| Order placed | Customer (in-app + email), Seller (in-app) |
| Order confirmed | Customer (in-app + email) |
| Order shipped | Customer (in-app + email + SMS) |
| Order delivered | Customer (in-app) |
| Order cancelled | Customer (in-app + email), Seller (in-app) |
| Return approved | Customer (in-app + email) |
| Refund processed | Customer (in-app + email) |
| KYC approved/rejected | Seller (in-app + email) |
| Withdrawal approved/rejected | Seller (in-app + email) |
| New review received | Seller (in-app) |

**FR-13.2 Delivery**
- All email and SMS notifications are delivered asynchronously via Bull queue workers.
- Failed deliveries are retried up to 3 times with exponential backoff.
- Delivery failures are logged but do not affect the originating API response.

**FR-13.3 Read State**
- `PATCH /notifications/:id/read` and `PATCH /notifications/read-all` mark notifications as read.
- Unread count is returned in `GET /users/me` response.

---

### FR-14: Referral System

**FR-14.1 Referral Code**
- Every user is assigned a unique 8-character alphanumeric referral code on account creation.
- The code is exposed in `GET /users/me`.

**FR-14.2 Applying a Referral**
- `POST /referrals/apply { "code": "ABC12345" }` can only be called once per user, within 24 hours of account creation.
- The referrer's `id` is stored in `users.referred_by`.
- A `referrals` row is created with `status = 'pending'`.

**FR-14.3 Reward Trigger**
- The referral reward is credited when the referred user completes their first order (payment confirmed).
- Reward amount is configurable (default ₹50 credited to referrer's wallet).
- `referrals.status` transitions to `'rewarded'`.

---

### FR-15: Support Tickets

**FR-15.1 Ticket Creation**
- Any authenticated user may create a support ticket.
- Optional `order_id` links the ticket to a specific order.
- `priority` defaults to `'medium'`; customers cannot set `'high'` — only admin can escalate.

**FR-15.2 Ticket Lifecycle**
- Status flow: `open → in_progress → resolved → closed`.
- Only admin can transition status.
- Customers can view their own tickets and add comments (comments table not in current schema — treated as ticket updates via `PATCH /support/:id`).

---

### FR-16: Admin Dashboard

**FR-16.1 Platform Stats**
- `GET /admin/dashboard` returns:
  - Total users (by role)
  - Total orders (by status)
  - Gross merchandise value (GMV) for current month and all-time
  - Platform commission earned (current month and all-time)
  - Pending KYC submissions count
  - Pending withdrawal requests count
  - Open support tickets count

**FR-16.2 Earnings Report**
- `GET /admin/earnings?from=2025-01-01&to=2025-01-31` returns daily breakdown of `platform_earnings`.

**FR-16.3 Commission Configuration**
- `PATCH /admin/config/commission { "default_rate": 12.0 }` updates the default commission rate for new sellers.
- Does not retroactively change existing sellers' rates.

---

## User Flows

### Customer Flow

```
1. Register / Login
   └─ Enter phone or email
   └─ Receive OTP (SMS or email)
   └─ Verify OTP → JWT issued
   └─ Profile created (wallet auto-created)

2. Browse & Discover
   └─ Search by keyword, filter by category / price / rating
   └─ View product detail page (images, variants, reviews)
   └─ View seller store page

3. Cart Management
   └─ Select variant (size, color) → Add to cart
   └─ Update quantity or remove items
   └─ Cart persists across sessions

4. Checkout
   └─ Enter / select shipping address
   └─ Apply coupon code (optional)
   └─ Select payment method (UPI / card / COD)
   └─ Review order summary → Place order
   └─ Redirected to payment gateway (if not COD)
   └─ Payment confirmed → Order created

5. Order Tracking
   └─ View order list → Select order
   └─ See status timeline (confirmed → shipped → delivered)
   └─ View tracking number and carrier

6. Post-Delivery
   └─ Submit review (rating + text + images)
   └─ Initiate return within 7 days (if eligible)

7. Support
   └─ Create support ticket (optionally linked to order)
   └─ Track ticket status
```

### Seller Flow

```
1. Onboard as Seller
   └─ Register as customer → Call /sellers/onboard
   └─ Submit KYC (PAN, GST, document upload)
   └─ Add bank details
   └─ Await admin KYC approval

2. Product Management
   └─ Create product (name, category, price, description)
   └─ Add variants (size/color/material + price + stock)
   └─ Upload product images (up to 8)
   └─ Submit for approval (status: draft → awaiting admin)
   └─ Product goes live after admin approval

3. Order Fulfillment
   └─ Receive notification of new order
   └─ Confirm order (processing)
   └─ Ship order (enter tracking number)
   └─ Mark delivered

4. Returns Handling
   └─ Receive return request notification
   └─ Approve or reject return with reason
   └─ Arrange reverse pickup

5. Earnings & Wallet
   └─ View earnings dashboard (per order item)
   └─ See wallet balance (settled earnings minus withdrawals)
   └─ Request withdrawal (min ₹100, bank details required)
   └─ Track withdrawal status
```

### Admin Flow

```
1. Account Setup
   └─ Created via CLI script (no API registration)
   └─ Login with email + password (not OTP)

2. Seller Management
   └─ Review KYC submissions (view documents via signed S3 URL)
   └─ Approve or reject KYC with reason
   └─ Set per-seller commission rate override

3. Product Moderation
   └─ Review products in 'draft' status
   └─ Approve (→ active) or reject with reason

4. Order Management
   └─ View all orders with filters (status, date, seller)
   └─ Override order status if needed
   └─ Handle escalated cancellations

5. Financial Management
   └─ View platform earnings report
   └─ Approve or reject seller withdrawal requests
   └─ Configure default commission rate

6. User Management
   └─ View all users with role filter
   └─ Deactivate / reactivate accounts

7. Coupon Management
   └─ Create, activate, deactivate, delete coupons

8. Support
   └─ View and manage all support tickets
   └─ Update ticket status and priority
```

---

## Edge Cases and Failure Scenarios

### Authentication

| Scenario | Expected Behaviour |
|---|---|
| OTP requested for unregistered phone | OTP sent; user created on verify (find-or-create) |
| OTP requested 4th time within 1 hour | `429 Too Many Requests` with `Retry-After` header |
| OTP submitted after 5-minute expiry | `401 Unauthorized { "error": "Invalid or expired OTP" }` |
| Refresh token used after logout | `401 Unauthorized` (token in Redis blocklist) |
| Admin login with wrong password | `401 Unauthorized`; no OTP fallback |
| Deactivated user attempts login | OTP verified successfully but `403 Forbidden` returned with `{ "error": "Account deactivated" }` |

### Inventory and Orders

| Scenario | Expected Behaviour |
|---|---|
| Two customers checkout the last unit simultaneously | Row-level lock ensures only one succeeds; second gets `409 Conflict { "error": "Insufficient stock", "sku": "..." }` |
| Cart item becomes out-of-stock before checkout | Checkout validation returns `422` listing unavailable items; customer must remove them |
| Payment gateway timeout during checkout | Order remains `pending`; inventory stays reserved for 30 minutes; reconciliation job resolves |
| Duplicate payment webhook received | Idempotency check on `gateway_ref`; second webhook returns `200 OK` with no state change |
| Customer cancels after order is shipped | `422 Unprocessable Entity { "error": "Cannot cancel shipped order. Initiate a return instead." }` |
| Seller marks delivered but customer disputes | Customer initiates return; admin can override order status |
| Return requested after 7-day window | `422 Unprocessable Entity { "error": "Return window has expired" }` |
| Return requested for already-returned item | `409 Conflict { "error": "Return already exists for this item" }` |

### Payments and Wallet

| Scenario | Expected Behaviour |
|---|---|
| Payment fails after inventory reserved | Reservation held for 30 min; reconciliation job releases if payment not retried |
| Seller wallet balance insufficient for refund debit | Refund still processed; seller wallet goes to negative (flagged for admin review) |
| Withdrawal requested exceeding wallet balance | `422 Unprocessable Entity { "error": "Insufficient wallet balance" }` |
| Commission settlement fails mid-transaction | Transaction rolled back; retry via Bull job with exponential backoff (max 5 retries) |
| Coupon used_count reaches usage_limit between validate and apply | Atomic increment inside order transaction; if limit exceeded, order fails with `422` |

### Seller and KYC

| Scenario | Expected Behaviour |
|---|---|
| Seller tries to publish product before KYC approval | Product remains in `draft`; `403 Forbidden` if attempting to set `active` directly |
| Seller submits KYC with invalid PAN format | `422 Unprocessable Entity` with field-level validation error |
| KYC document upload exceeds 5 MB | `413 Payload Too Large` |
| Seller account deactivated with active orders | Existing orders continue; seller cannot log in or create new products |
| Two sellers attempt same shop_name | `409 Conflict { "error": "Shop name already taken" }` |

### Reviews

| Scenario | Expected Behaviour |
|---|---|
| Customer reviews before delivery | `403 Forbidden { "error": "Review only allowed after delivery" }` |
| Customer submits second review for same order+product | `409 Conflict` (unique constraint on `product_id, user_id, order_id`) |
| Review image upload fails | Review saved without images; partial failure does not block review submission |

---

## API Endpoint Definitions

### Complete Endpoint Reference

| Method | Path | Auth Required | Role | Description |
|---|---|---|---|---|
| POST | `/api/auth/request-otp` | No | Any | Request OTP |
| POST | `/api/auth/verify-otp` | No | Any | Verify OTP, get tokens |
| POST | `/api/auth/admin-login` | No | Admin | Admin email+password login |
| POST | `/api/auth/refresh` | Cookie | Any | Refresh access token |
| POST | `/api/auth/logout` | JWT | Any | Revoke refresh token |
| GET | `/api/users/me` | JWT | Any | Own profile |
| PUT | `/api/users/me` | JWT | Any | Update own profile |
| GET | `/api/users` | JWT | Admin | List users |
| GET | `/api/users/:id` | JWT | Admin | Get user by ID |
| PATCH | `/api/users/:id/status` | JWT | Admin | Activate/deactivate |
| POST | `/api/sellers/onboard` | JWT | Customer | Become a seller |
| GET | `/api/sellers/me` | JWT | Seller | Own seller profile |
| PUT | `/api/sellers/kyc` | JWT | Seller | Submit KYC |
| PUT | `/api/sellers/bank` | JWT | Seller | Update bank details |
| GET | `/api/sellers` | JWT | Admin | List all sellers |
| PATCH | `/api/sellers/:id/kyc` | JWT | Admin | Approve/reject KYC |
| PATCH | `/api/sellers/:id/commission` | JWT | Admin | Set commission rate |
| GET | `/api/categories` | No | Any | List categories (tree) |
| POST | `/api/categories` | JWT | Admin | Create category |
| GET | `/api/products` | No | Any | Search/list products |
| GET | `/api/products/:id` | No | Any | Product detail |
| POST | `/api/products` | JWT | Seller | Create product |
| PUT | `/api/products/:id` | JWT | Seller | Update product |
| DELETE | `/api/products/:id` | JWT | Seller | Delete product |
| POST | `/api/products/:id/variants` | JWT | Seller | Add variant |
| PUT | `/api/products/:id/variants/:vid` | JWT | Seller | Update variant |
| POST | `/api/products/:id/images` | JWT | Seller | Upload images |
| PATCH | `/api/products/:id/status` | JWT | Admin | Approve/reject product |
| GET | `/api/cart` | JWT | Customer | Get cart |
| POST | `/api/cart` | JWT | Customer | Add item to cart |
| PUT | `/api/cart/:itemId` | JWT | Customer | Update cart item qty |
| DELETE | `/api/cart/:itemId` | JWT | Customer | Remove cart item |
| DELETE | `/api/cart` | JWT | Customer | Clear cart |
| POST | `/api/orders` | JWT | Customer | Place order |
| GET | `/api/orders` | JWT | Any | List orders (role-filtered) |
| GET | `/api/orders/:id` | JWT | Any | Order detail |
| PATCH | `/api/orders/:id/status` | JWT | Seller/Admin | Update order status |
| POST | `/api/orders/:id/cancel` | JWT | Customer | Cancel order |
| POST | `/api/payments/confirm` | JWT | Customer | Confirm payment |
| POST | `/api/payments/webhook` | HMAC | — | Gateway webhook |
| GET | `/api/payments/:orderId` | JWT | Any | Payment status |
| GET | `/api/shipping/:orderId` | JWT | Any | Tracking info |
| PUT | `/api/shipping/:orderId` | JWT | Seller/Admin | Update tracking |
| POST | `/api/returns` | JWT | Customer | Initiate return |
| GET | `/api/returns` | JWT | Any | List returns |
| PATCH | `/api/returns/:id/status` | JWT | Seller/Admin | Approve/reject return |
| POST | `/api/reviews` | JWT | Customer | Submit review |
| GET | `/api/reviews/product/:id` | No | Any | Product reviews |
| DELETE | `/api/reviews/:id` | JWT | Admin | Delete review |
| POST | `/api/coupons` | JWT | Admin | Create coupon |
| GET | `/api/coupons` | JWT | Admin | List coupons |
| POST | `/api/coupons/validate` | JWT | Customer | Validate coupon |
| DELETE | `/api/coupons/:id` | JWT | Admin | Delete coupon |
| GET | `/api/wallet` | JWT | Any | Wallet balance + history |
| POST | `/api/wallet/withdraw` | JWT | Seller | Request withdrawal |
| GET | `/api/wallet/withdrawals` | JWT | Admin | List withdrawals |
| PATCH | `/api/wallet/withdrawals/:id` | JWT | Admin | Approve/reject withdrawal |
| GET | `/api/notifications` | JWT | Any | Get notifications |
| PATCH | `/api/notifications/:id/read` | JWT | Any | Mark one as read |
| PATCH | `/api/notifications/read-all` | JWT | Any | Mark all as read |
| POST | `/api/support` | JWT | Any | Create ticket |
| GET | `/api/support` | JWT | Any | List own tickets |
| GET | `/api/support/:id` | JWT | Any | Ticket detail |
| PATCH | `/api/support/:id/status` | JWT | Admin | Update ticket status |
| GET | `/api/referrals` | JWT | Any | Referral stats |
| POST | `/api/referrals/apply` | JWT | Customer | Apply referral code |
| GET | `/api/admin/dashboard` | JWT | Admin | Platform stats |
| GET | `/api/admin/earnings` | JWT | Admin | Earnings report |
| PATCH | `/api/admin/config/commission` | JWT | Admin | Update default rate |

---

## Business Logic Rules

### Commission Rules
- Commission is calculated at order placement time using the seller's rate at that moment (snapshot).
- Commission rate changes do not affect existing orders.
- `commission + seller_payout = total_price` must hold exactly (use `DECIMAL(10,2)` arithmetic; round commission up, seller_payout = total - commission).
- Platform commission is recorded per `order_item`, not per `order`.

### Pricing Rules
- `product_variants.price` is the selling price (what the customer pays).
- `products.mrp` is the maximum retail price (must be ≥ `base_price`).
- Discount percentage shown to customer = `((mrp - price) / mrp) × 100`.
- Coupon discount is applied to the order subtotal (sum of all `order_item.total_price`), not to individual items.

### Inventory Rules
- Available stock = `inventory.quantity - inventory.reserved`.
- `reserved` is incremented at order placement; decremented at order confirmation (actual deduction) or cancellation (release).
- `quantity` is decremented at order confirmation.
- Inventory can never go below 0. Any operation that would violate this is rejected.

### Return Window Rules
- Return window = 7 calendar days from `shipping.delivered_at`.
- If `shipping.delivered_at` is null (delivery not confirmed), returns are not allowed.
- Return window is per `order_item`, not per `order` (different items may have different delivery dates).

### Referral Rules
- A user can only be referred once (enforced by `UNIQUE` on `referrals.referred_id`).
- Self-referral is rejected (referrer_id ≠ referred_id check).
- Referral code application window: 24 hours from account creation.
- Reward is credited only on first completed order (payment confirmed), not on order placement.

### Seller Eligibility Rules
- A seller must have `kyc_status = 'approved'` to publish products.
- A seller must have bank details on file to request withdrawals.
- Minimum withdrawal amount: ₹100.
- A seller cannot have more than 3 pending withdrawal requests simultaneously.

---

## Non-Functional Requirements

### NFR-1: Security

| Requirement | Specification |
|---|---|
| Authentication | JWT (RS256 algorithm); access token 15 min; refresh token 7 days in httpOnly cookie |
| OTP Security | 6-digit CSPRNG; Redis TTL 5 min; rate limit 3/hour/identifier; constant-time comparison |
| Admin Access | CLI-only creation; bcrypt cost ≥ 12; no admin registration API |
| Transport | HTTPS enforced; HSTS header; TLS 1.2+ only |
| Input Validation | All inputs validated with Joi before reaching service layer; SQL injection prevented by Sequelize parameterized queries |
| File Uploads | MIME type validation; max 5 MB; virus scan before S3 upload (ClamAV or cloud service) |
| KYC Documents | Stored in private S3 bucket; accessed only via signed URLs (15-min expiry) |
| Payment Webhooks | HMAC-SHA256 signature validation; idempotency via `gateway_ref` |
| Secrets | All secrets in environment variables; never in code or logs |
| CORS | Restricted to frontend domain in production |
| Headers | `helmet` middleware: CSP, X-Frame-Options, X-Content-Type-Options |
| Logging | No PII (phone, email, PAN) in application logs; use masked identifiers |

### NFR-2: Performance

| Requirement | Target |
|---|---|
| API response time (p95) | < 200ms for read endpoints; < 500ms for write endpoints |
| OTP delivery time | < 3 seconds (SMS); < 5 seconds (email) |
| Product search | < 300ms for full-text search with filters (MySQL FULLTEXT index) |
| Concurrent users | Support 10,000 concurrent users without degradation |
| Order placement throughput | 500 orders/minute sustained |
| Cache hit rate | > 80% for product listing and category tree endpoints |
| Image upload | < 3 seconds for 5 MB image to S3/Cloudinary |

### NFR-3: Scalability

- The API server is stateless (no in-process session state); horizontal scaling via load balancer is supported.
- Redis is used for all shared state (OTP, token blocklist, cache).
- Bull queues allow worker processes to scale independently of the API server.
- MySQL read replicas can be added for read-heavy endpoints (product search, order listing) without code changes (Sequelize supports read/write splitting).
- Product search should migrate to Elasticsearch when catalog exceeds 500,000 active products.
- All list endpoints enforce pagination (default 20, max 100 per page).

### NFR-4: Reliability

| Requirement | Specification |
|---|---|
| Uptime SLA | 99.9% (< 8.7 hours downtime/year) |
| Data durability | MySQL with daily automated backups; point-in-time recovery enabled |
| Queue reliability | Bull with Redis persistence; failed jobs retried up to 3 times with exponential backoff |
| Payment reconciliation | Reconciliation job every 15 minutes for stuck `pending` orders |
| Commission settlement retry | Up to 5 retries with exponential backoff on settlement failure |
| Graceful shutdown | API server drains in-flight requests before shutdown (30-second timeout) |

### NFR-5: Observability

- Structured JSON logging via `winston` with request ID correlation.
- All API requests logged with: method, path, status code, response time, user ID (masked).
- Error events include stack trace and request context.
- Health check endpoint: `GET /health` returns `200 OK { "status": "ok", "db": "ok", "redis": "ok" }`.
- Metrics exposed for Prometheus scraping: request rate, error rate, response time histograms, queue depth.

### NFR-6: Compliance

- PAN and bank account numbers stored encrypted at rest (AES-256-GCM).
- KYC documents stored in private S3 bucket with access logging enabled.
- User data deletion: `DELETE /users/me` anonymises PII (email, phone replaced with hashed values) while preserving order history for financial audit.
- All financial transactions (orders, payments, earnings, withdrawals) are immutable — no hard deletes.

### NFR-7: Availability and Deployment

- Zero-downtime deployments via rolling updates.
- Database migrations run separately from application deployment (Sequelize migrations).
- Feature flags for gradual rollout of new features.
- Staging environment mirrors production configuration.

---

## Acceptance Criteria Summary

| Feature | Acceptance Criteria |
|---|---|
| OTP Auth | User can register and login with phone or email; OTP expires in 5 min; rate limit enforced |
| Admin Creation | Admin can only be created via CLI; no API endpoint exists for admin registration |
| Seller KYC | Seller cannot publish products until KYC approved; admin can approve/reject with reason |
| Product Variants | Product can have multiple variants with different sizes, colors, prices, and stock levels |
| Inventory | Overselling is impossible; concurrent checkout race condition handled via row-level locks |
| Order Flow | Full lifecycle from placement to delivery works end-to-end; status transitions enforced |
| Commission | Commission calculated at order time; seller wallet credited on delivery; platform earnings recorded |
| Returns | Return only allowed within 7 days of delivery; refund credited to customer wallet |
| Coupons | Coupon validated and applied atomically; usage limit enforced under concurrent load |
| Notifications | All key events trigger in-app + email/SMS notifications asynchronously |
| Referrals | Referral reward credited only on first completed order; self-referral rejected |
| Wallet | Balance never goes negative; all operations transactional |
