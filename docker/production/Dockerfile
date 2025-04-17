# Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /code

# Install system dependencies needed for build
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
 && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements/base.txt requirements/production.txt /code/requirements/
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /code/wheels -r /code/requirements/production.txt

# Stage 2: Final image
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /code

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
 && rm -rf /var/lib/apt/lists/*

# Copy wheels and install
COPY --from=builder /code/wheels /wheels
COPY --from=builder /code/requirements/production.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache /wheels/*

# Copy project
COPY . /code/

EXPOSE 8000

CMD ["gunicorn", "gab_bookstore.wsgi:application", "--bind", "0.0.0.0:8000"]
