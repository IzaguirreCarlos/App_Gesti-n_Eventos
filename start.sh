#!/usr/bin/env bash
set -o errexit

echo "🚀 Starting EventPro with Gunicorn..."
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:$PORT \
  --workers ${WEB_CONCURRENCY:-2} \
  --worker-class sync \
  --timeout 120 \
  --keep-alive 5 \
  --max-requests 1000 \
  --max-requests-jitter 50 \
  --access-logfile - \
  --error-logfile - \
  --log-level info
