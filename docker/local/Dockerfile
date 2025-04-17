FROM python:3.12-slim

# Prevent Python from writing pyc files and buffers stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /code

# Install system dependencies needed to build psycopg2 (libpq-dev and build-essential)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy requirement files
COPY requirements/base.txt requirements/dev.txt /code/requirements/

# Install dev dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /code/requirements/dev.txt

# Copy entire codebase
COPY . /code/

EXPOSE 8000

CMD ["/bin/bash"]
