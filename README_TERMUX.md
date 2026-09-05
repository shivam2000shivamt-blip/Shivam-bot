## 3.0.9 Language System

The main user menu includes a 🌐 Language button. Users can choose from 13 languages and the selection is stored per user. The selected locale is used throughout the main menu and shopping screens. Product/category/plan names and descriptions support per-language content via the owner-only **Content Languages** admin screen. Coupon codes and referral links are kept exactly as entered/generated.

# SHIVAM STORE BOT 3.0.8

Telegram digital-product store bot for Termux/Render.

## Referral system
- Users get a unique Telegram referral link from the Referral button.
- Self-referrals and duplicate referral attribution are blocked.
- A referral becomes successful after the referred user completes their first product purchase.
- The owner can set the exact reward amount from Admin → Referral Management.
- Each successful referral credits exactly that configured amount to the referrer wallet once.
- Referral rewards appear in wallet history and can be used for store purchases.
- Admin can view total referrals, successful referrals, total rewards, top referrers and recent referral activity.

## Security
- Owner-only admin access.
- Automatic UTR/Gmail-IMAP verification is fail-closed when trusted senders are not configured.
- Payment matching uses UTR, amount scope, recipient and trusted sender checks.
- SQLite snapshot backups and payment idempotency are supported.

## Note
Live Telegram/Gmail/bank-email behavior still requires testing in the actual deployment environment. No software can honestly be guaranteed 100% bug-free without live environment testing.


## 3.0.11 User Settings & Menu
- More is replaced by Settings without changing the existing button sizing/layout.
- Selling Proof + Tutorial provides separate direct Tutorial and Selling Proof channel buttons.
- User Settings includes the agreed account, security, notification, wallet, shopping, referral, support, about, reset, and theme preference sections.
- Bot Password Lock is per-user; passwords are stored as PBKDF2 hashes with unique salts, and password messages are deleted after receipt.
- A successful unlock returns to the full normal start/welcome screen.
- Theme Preference is stored per user; Telegram chat theme itself cannot be forced by a bot.


## 3.0.12
- Settings now exposes Account, Security, Notifications, Wallet, Shopping, Referral, Support, About, Reset Settings and Theme Preference.
- Referral link is rendered as a Telegram-blue clickable HTML link.
- Referral Share Message is owner-configurable (up to Telegram message length limits) and is used by the Share Referral button.
- Notification categories have independent toggles.
- Password remember duration is persisted per user and failed-password cooldown protection is enforced.
