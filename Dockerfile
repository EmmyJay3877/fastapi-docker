# pull the official docker image
FROM python:3.10-slim

# set work directory
WORKDIR /backend

RUN apt-get update && \
    apt-get install -y libpq-dev gcc g++ && \
    apt-get install -y --no-install-recommends build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# create virtual environment
RUN python3 -m venv /backend/venv
# activate virtual environment
ENV PATH="/backend/venv/bin:$PATH"

RUN apt update

RUN apt-get install -y python3-pip

# install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir --upgrade -r /backend/requirements.txt

# copy project
COPY ./app /app

COPY ./.env .env

RUN alembic init alembic

COPY ./alembic/env.py ./alembic/env.py

COPY alembic.ini alembic.ini

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1