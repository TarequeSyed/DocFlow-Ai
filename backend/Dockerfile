FROM python:3.12-slim

# Avoid writing pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install native compilation libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Leverage Docker layer caching for python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files (leveraging .dockerignore to skip dev caches)
COPY . .

EXPOSE 8000

# Run without --reload by default in production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
