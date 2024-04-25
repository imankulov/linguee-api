# First stage: Install poetry and dependencies
FROM python:3.12-slim AS builder

# Install system dependencies
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for poetry
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_NO_INTERACTION=1
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy only requirements to cache them in docker layer
WORKDIR /app
COPY pyproject.toml poetry.lock /app/

# Install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
# and install spacy's en_core_web_sm
RUN poetry install --only main --no-root


# Second stage: Copy from builder and run
FROM python:3.12-slim AS runner

# Copy virtualenv from builder
COPY --from=builder /app/.venv /app/.venv

WORKDIR /app

# Ensure we use the virtualenv
ENV PATH="/app/.venv/bin:$PATH"

# Copy the content of the app
COPY . /app/

# Declare port FastAPI will use
EXPOSE 8000

# Declare the VOLUME and use it as a cache directory
VOLUME /cache
ENV CACHE_DIRECTORY=/cache

# Command to run on container start
CMD ["uvicorn", "linguee_api.api:app", "--host", "0.0.0.0", "--port", "8000"]
