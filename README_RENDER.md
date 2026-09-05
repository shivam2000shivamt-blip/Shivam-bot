# SHIVAM STORE BOT 3.0.12 — Render Deployment

This package is the original SHIVAM STORE BOT 3.0.12 packaged for Render as a Docker Web Service.

## Render
1. Upload these files to a GitHub repository.
2. In Render, create **New → Web Service** and select the repository.
3. Choose **Docker** runtime (or use the included `render.yaml` Blueprint).
4. Set the required environment variables:
   - `BOT_TOKEN` = Telegram bot token
   - `ADMIN_USER_ID` = numeric Telegram owner/admin ID
5. Keep `DB_PATH=/var/data/shivam_store.sqlite3` when using the included persistent disk Blueprint.
6. Deploy.

The bot starts a small HTTP health server on Render's injected `PORT`. Health endpoints are `/`, `/health`, `/healthz`, and `/api/health`.

## Important
- Do not commit `.env` or real tokens to GitHub.
- Render Free instances are not suitable for guaranteed 24/7 bot uptime. The included Blueprint uses a paid Starter service and a persistent disk for SQLite.
- Gmail/IMAP verification remains optional and requires valid credentials/app password and trusted sender settings.
