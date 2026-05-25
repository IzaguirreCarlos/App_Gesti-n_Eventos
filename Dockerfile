FROM python:3.12-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    # PostgreSQL client
    libpq-dev \
    # Compiler (psycopg2-binary build)
    gcc \
    # Pillow dependencies
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    # Utilities
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Upgrade pip first
RUN pip install --upgrade pip

# Install Python dependencies
COPY requirements.txt .
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files (production settings)
RUN python manage.py collectstatic --noinput --settings=config.settings.production || true

# Create non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", \
     "--timeout", "120", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
