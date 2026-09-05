#!/usr/bin/env sh
set -eu
python -m py_compile bot.py
exec python bot.py
