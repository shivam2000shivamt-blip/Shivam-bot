#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")"

if [ ! -f .env ]; then
  echo "ERROR: .env nahi mila. Pehle: bash setup_termux.sh"
  exit 1
fi

python -m py_compile bot.py
exec python bot.py
