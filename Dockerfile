FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --timeout 60 --retries 5 -r requirements.txt

COPY bot.py ./bot.py
COPY README.md ./README.md
COPY .env.example ./.env.example
COPY tests.py ./tests.py
COPY backup.sh ./backup.sh

RUN python -m py_compile bot.py && chmod +x backup.sh

# Render injects PORT. The bot also starts a tiny health server on that port.
CMD ["python", "bot.py"]
