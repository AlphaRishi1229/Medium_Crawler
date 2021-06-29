FROM python:3.8.2-slim-buster as pbase

WORKDIR /
RUN apt update \
    && apt install bash libpq-dev gcc -y

RUN python -m venv .venv \
	&& .venv/bin/pip install --no-cache-dir -U pip setuptools

ADD requirements.txt .
RUN .venv/bin/pip install --no-cache-dir -r requirements.txt
COPY . /srv/crawler-medium/
RUN cd /srv/crawler-medium/

FROM python:3.8.2-slim-buster as runtime
WORKDIR /srv/crawler-medium
RUN apt update \
    && apt install -y --no-install-recommends vim libpq-dev -y \
    && rm -rf /var/lib/apt/lists/*
COPY --from=pbase /srv/crawler-medium /srv/crawler-medium
COPY --from=pbase /.venv /.venv
EXPOSE 80

ENV PATH="/.venv/bin:$PATH"

# Added PYTHONPATH for alembic upgrade and render alembic.ini
ENV PYTHONPATH /srv/crawler-medium/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
