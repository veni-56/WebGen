FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create required directories
RUN mkdir -p generated static/uploads

# Non-root user for security
RUN useradd -m -u 1000 webgen && chown -R webgen:webgen /app
USER webgen

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

# Environment defaults
ENV FLASK_ENV=production \
    PORT=5000 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Production server
CMD gunicorn app:app \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
