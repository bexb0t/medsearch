# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /medsearch

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       curl \
       build-essential \
       pkg-config \
       default-libmysqlclient-dev \
       gettext-base \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:${PATH}"

# Copy only the dependency files to the working directory
COPY pyproject.toml poetry.lock* /medsearch/

# Install dependencies in .venv directory
RUN poetry config virtualenvs.in-project true && \
    poetry install --no-root --no-interaction

# Copy the rest of the application code
COPY src /medsearch/src
COPY tests /medsearch/tests
COPY alembic /medsearch/alembic
