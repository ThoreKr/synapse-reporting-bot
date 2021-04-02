FROM python:3.9-slim-buster AS builder

RUN mkdir -p /app
RUN apt-get update && apt-get install -y git gcc python3-dev libpq-dev

WORKDIR /app
RUN pip --no-cache-dir install --upgrade pip setuptools wheel

COPY . /app

RUN pip wheel . --wheel-dir /wheels --find-links /wheels


#
FROM python:3.9-slim-buster

COPY --from=builder /wheels /wheels
RUN apt-get update && apt-get install -y libpq-dev && apt-get clean

RUN pip --no-cache-dir install --find-links /wheels --no-index reporting-bot


CMD reporting-bot
