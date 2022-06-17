FROM python:3.10

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
WORKDIR /app
COPY . .
RUN /root/.poetry/bin/poetry install
EXPOSE 8000
CMD /root/.poetry/bin/poetry run uvicorn linguee_api.api:app --host 0.0.0.0 --port 8000
