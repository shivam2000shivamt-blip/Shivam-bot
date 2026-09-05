# SHIVAM STORE BOT 3.0.11 — Premium User Settings

- Main menu keeps the Shop Now top button, 4x2 middle action grid, and Language bottom button; More is replaced by Settings.
- Selling Proof + Tutorial opens separate direct Telegram links for Tutorial and Selling Proof when configured.
- Added user Settings sections for Account, Security, Notifications, Wallet, Shopping, Referral, Support/Help, About/Policies, Reset Preferences, and Theme Preference.
- Added per-user Bot Password Lock with PBKDF2 password hashing, change/disable/lock-now controls, remember-unlock duration, and password-message cleanup.
- Correct password restores the complete normal start/welcome screen and main menu.

# SHIVAM STORE BOT 3.0.9 — Language Hardened

- Added visible 🌐 Language button to the main user menu.
- Added 13 selectable languages: English, Hindi, Bengali, Telugu, Marathi, Tamil, Gujarati, Kannada, Malayalam, Punjabi, Odia, Urdu and Assamese.
- User language is persisted in SQLite and survives restart.
- Main menu and shopping flow use the selected language.
- Category/product/plan name and description localization fields added with safe English fallback.
- Owner-only Content Languages screen lets the owner save localized product/category/plan text.
- Coupon codes remain unchanged and are never translated.
- Referral URLs/codes remain unchanged and are never translated.
- Added regression tests for language persistence and localization paths.

# CHANGELOG

## 3.0.8 — Referral & Wallet Rewards Hardened
- Added owner-controlled referral reward setting.
- Added user Referral screen with unique Telegram deep-link and share button.
- Added referral tracking with self-referral and duplicate-referral protection.
- Added exact once-only referral wallet credit on the referred user's first completed product purchase.
- Added referral wallet ledger entries and admin referral statistics/top referrers.
- Added admin Referral Management, Referral Users and Set Referral Reward controls.
- Referral reward is calculated in the same database transaction as successful product order approval/wallet purchase.
- Removed Coupon UI buttons from the store/admin panel as requested; legacy coupon database/code remains only for backward compatibility with old orders.
- Added offline regression coverage for referral registration, duplicate protection, exact reward credit and once-only payout.

# CHANGELOG

## 3.0.8 — Referral & Wallet Rewards Hardened
- Added owner-controlled referral reward setting.
- Added user Referral screen with unique Telegram deep-link and share button.
- Added referral tracking with self-referral and duplicate-referral protection.
- Added exact once-only referral wallet credit on the referred user's first completed product purchase.
- Added referral wallet ledger entries and admin referral statistics/top referrers.
- Added admin Referral Management, Referral Users and Set Referral Reward controls.
- Referral reward is calculated in the same database transaction as successful product order approval/wallet purchase.
- Removed Coupon UI buttons from the store/admin panel as requested; legacy coupon database/code remains only for backward compatibility with old orders.
- Added offline regression coverage for referral registration, duplicate protection, exact reward credit and once-only payout.

## 3.0.7 — Deep Payment + Reliability Hardening
- Payment matcher re-checks trusted sender policy at the final matching layer (defense in depth).
- Amount matching checks every occurrence of the submitted UTR, avoiding false negatives when an email repeats the UTR in a footer/summary.
- Failed-delivery retry now displays the newly allocated key expiry correctly when recovering an order that previously had no stock.
- `/imaptest` now reports missing trusted sender configuration as a failed readiness check.
- Admin health now exposes the last automatic payment-verifier error in addition to the last run time.
- UTR/RRN user prompts now consistently describe the supported 12–30 character format.

## 3.0.6 — Payment Security + Reliability Hardening
- Automatic verifier now fails closed unless trusted IMAP senders are configured.
- Sender matching supports exact email/domain boundaries; `fakebank.com` cannot satisfy `bank.com`.
- Payment amount is matched in the transaction block around the UTR; balance/limit/footer amounts cannot satisfy the order amount.
- UTR/RRN validation supports 12–30 alphanumeric characters and targeted IMAP search.
- Fulfillment performs a second expiry check inside the atomic transaction, preventing expiry-worker race approvals.
- Verified payments with no stock enter a recovery state, notify the user/admin, and can be retried after stock is added.
- QR payment Cancel/Status paths cleanly replace the photo screen instead of stacking text below it.
- IMAP verification uses one authenticated connection per cycle for multiple pending UTR searches.
- Added persistent `payment_events` idempotency records keyed by provider + email UID.
- Added IMAP last-run/health information to admin diagnostics.
- Scheduled broadcast processing has stale-worker recovery using `processing_at`.
- Admin database backup now uses SQLite online backup API + integrity check snapshot instead of copying the live WAL-mode database file.
- Added regression tests for sender spoofing, amount-scope false positives, expiry races, payment events and clean payment screens.

# CHANGELOG

## 3.0.5 — Single Screen + Admin Chat Cleanup
- `/start` is idempotent: repeated Start presses replace the previously tracked store screen instead of stacking menus.
- `/admin` opens one tracked admin screen.
- Admin text-entry messages (product, coupon, stock, pricing, links, searches, broadcasts, etc.) are deleted immediately after receipt.
- Temporary admin bot replies are tracked and removed when Logout is pressed.
- Logout reuses the current admin panel message as the single main store menu, avoiding duplicate menus.
- Store data such as created products/coupons/stock remains intact; only temporary admin chat UI is removed.


- Exact UTR server-side Gmail/IMAP search before verification.
- More robust payment-email parsing and header matching.
- Clean PENDING → VERIFIED/SUCCESS delivery message flow.
- Payment screen replaces the previous storefront screen and BACK returns cleanly to the menu.

## 3.0.3 — Premium Digital Store
- Product → Plan stock picker for clean per-plan key entry.
- Dedicated 🔑 Add Keys action beside every plan.
- Product-level 🚧 Maintenance Mode with database migration support.
- Maintenance blocks both UPI and Wallet purchase paths while preserving stock.
- Maintenance toggles are audit logged.

# Changelog

## 3.0.3-PREMIUM-DIGITAL-STORE
- Hardened Gmail/IMAP App Password normalization and non-destructive `/imaptest` diagnostic.
- Improved HTML email parsing/entity decoding for bank notifications.
- Rejects future-dated payment emails.
- Strengthened exact 12-digit UTR + exact amount + recipient matching.
- Increased recent IMAP message scan window to reduce missed alerts during busy inbox periods.
- Added defensive validation for callback IDs.
- Added Decimal-based monetary parsing/formatting for critical comparisons.
- Fixed SQLite connection lifecycle so every database context closes cleanly.
- Fixed backup file handle lifecycle.
- Added offline Gmail/IMAP regression tests.


## 3.0.1-STABLE-AUTO-PAY — 2026-09-04
- Fixed missing Add Category text handler.
- Fixed admin callback authorization whitelist so catalog/stock/coupon/risk/user/maintenance callbacks are not blocked by user verification.
- Fixed payment flow state so UTR mode starts only after VERIFY PAYMENT.
- Fixed pending-order expiry and added explicit expiry timestamps.
- Removed the legacy Web App UTR receiver/handler.
- Hardened stock import reporting and validation.

## 3.0.0-AUTO-PAY — 2026-09-04

### Payment changes
- Removed manual owner payment approval/rejection buttons from the payment verification flow.
- Changed UTR entry to a normal Telegram chat flow: clicking VERIFY PAYMENT prompts the user to send the 12-digit UTR in chat; removed the Web App UTR input and hosting requirement.
- Added automatic Gmail/IMAP payment verification.
- Verification requires a recent matching UTR and exact amount; strict recipient/UPI matching is enabled by default.
- Optional sender allow-list is supported.
- Duplicate UTRs are blocked and risk-flagged.
- Verification uncertainty never auto-delivers a product.
- Successful verification triggers atomic stock allocation and automatic delivery.
- Wallet deposits and reseller membership payments can also be automatically verified.
- Added a payment-status button; it never approves a payment manually.

### UI changes
- Removed Offers button/flow.
- Removed FAQ button/flow.
- Removed Refresh button.
- Final payment controls: UTR Number, PAYMENT, CANCEL PAYMENT, BACK.

### Reliability
- Gmail message scanning repeats over the recent lookback window instead of relying only on unread mail or a last-UID marker, so a payment email that arrived before the user submitted UTR can still match.
- Email timestamp is checked so old matching records are ignored.
- Amount matching is performed near the UTR occurrence to reduce false matches.
- Backup uses Python's SQLite online backup API plus integrity check.

### Deployment
- Termux remains the first target.
- Render/PostgreSQL remains the later production migration.


## 3.0.12
- Settings now exposes Account, Security, Notifications, Wallet, Shopping, Referral, Support, About, Reset Settings and Theme Preference.
- Referral link is rendered as a Telegram-blue clickable HTML link.
- Referral Share Message is owner-configurable (up to Telegram message length limits) and is used by the Share Referral button.
- Notification categories have independent toggles.
- Password remember duration is persisted per user and failed-password cooldown protection is enforced.
