FROM python:3.10

RUN curl -sSL https://install.python-poetry.org | python3 -
WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN /root/.local/bin/poetry install --no-root
EXPOSE 8000
COPY . .
RUN /root/.local/bin/poetry install

VOLUME /cache
ENV CACHE_DIRECTORY=/cache

CMD /root/.local/bin/poetry run uvicorn linguee_api.api:app --host 0.0.0.0 --port 8000
