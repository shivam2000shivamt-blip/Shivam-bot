#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")"
umask 077

echo "== SHIVAM STORE BOT SETUP =="

echo "[1/4] Checking Python..."
command -v python >/dev/null 2>&1 || { echo "ERROR: Python nahi mila. Termux me: pkg install python -y"; exit 1; }
python --version

echo "[2/4] Installing bot dependencies..."
# Termux manages its own pip package. Do NOT run 'pip install --upgrade pip'
# because Termux intentionally blocks replacing its bundled pip.
python -m pip install --disable-pip-version-check --prefer-binary -r requirements.txt

echo "[3/4] Configuration"
if [ -f .env ]; then
  echo ".env already exists; existing configuration ko preserve kiya jayega."
else
  read -rsp "BotFather BOT_TOKEN (screen par nahi dikhega): " BOT_TOKEN
  echo
  read -rp "Numeric OWNER/ADMIN_USER_ID: " ADMIN_USER_ID
  read -rp "UPI_ID (optional; Admin Settings se baad me set kar sakte hain): " UPI_ID
  read -rp "Enable Gmail/IMAP auto payment verification? (1/0): " IMAP_ENABLED
  read -rp "Gmail address (blank = configure later): " IMAP_USERNAME
  if [ "$IMAP_ENABLED" = "1" ]; then
    read -rsp "Gmail App Password (screen par nahi dikhega): " IMAP_APP_PASSWORD
    echo
  else
    IMAP_APP_PASSWORD=""
  fi

  if [ -z "$BOT_TOKEN" ]; then
    echo "ERROR: BOT_TOKEN khali nahi ho sakta."
    exit 1
  fi
  if ! [[ "$ADMIN_USER_ID" =~ ^[0-9]+$ ]]; then
    echo "ERROR: ADMIN_USER_ID sirf ek numeric Telegram user ID hona chahiye."
    exit 1
  fi

  cat > .env <<ENVEOF
BOT_TOKEN=$BOT_TOKEN
ADMIN_USER_ID=$ADMIN_USER_ID
STORE_TIMEZONE=Asia/Kolkata
UPI_ID=$UPI_ID
IMAP_ENABLED=$IMAP_ENABLED
IMAP_HOST=imap.gmail.com
IMAP_PORT=993
IMAP_USERNAME=$IMAP_USERNAME
IMAP_APP_PASSWORD=$IMAP_APP_PASSWORD
IMAP_FOLDER=INBOX
IMAP_POLL_SECONDS=15
IMAP_LOOKBACK_MINUTES=30
IMAP_ALLOWED_SENDERS=alerts@yourbank.example
IMAP_REQUIRE_TRUSTED_SENDER=1
IMAP_REQUIRE_RECIPIENT_MATCH=1
ENVEOF
  unset BOT_TOKEN ADMIN_USER_ID UPI_ID IMAP_ENABLED IMAP_USERNAME IMAP_APP_PASSWORD
  chmod 600 .env
fi

chmod +x run.sh setup_termux.sh backup.sh

echo "[4/4] Syntax + self-tests..."
python -m py_compile bot.py tests.py
python tests.py

echo
echo "========================================"
echo "Setup complete."
echo "Bot start: ./run.sh"
echo "Version check in Telegram: /version"
echo "Owner admin check in Telegram: /admin"
echo "========================================"
