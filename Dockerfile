# Use Python slim image
FROM python:3.12-slim

# Install wget for health checks
RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv pip install --system -r pyproject.toml

# Copy entire assistant-app directory
COPY assistant-app/ /app/assistant-app/

# Set working directory to where app.py is located
WORKDIR /app/assistant-app

# Expose port
EXPOSE 8000

# Run wait script then start app (both in same shell)
CMD ["/bin/bash", "-c", "sleep 15 && uvicorn app:app --host 0.0.0.0 --port 8000"]