FROM python:3.12-slim AS builder

RUN mkdir -p /app
RUN apt-get update && apt-get install -y git gcc python3-dev libpq-dev

WORKDIR /app
RUN pip --no-cache-dir install --upgrade setuptools wheel

COPY . /app

RUN pip wheel . --wheel-dir /wheels --find-links /wheels


#
FROM python:3.12-slim

ARG UNAME=reporting_bot
ARG UID=993
ARG GID=993
RUN groupadd -g $GID -o $UNAME
RUN useradd -m -u $UID -g $GID -o -s /bin/bash $UNAME


COPY --from=builder /wheels /wheels
RUN apt-get update && apt-get install -y libpq-dev && apt-get clean

WORKDIR /usr/src/app
RUN chown -R $UNAME:$UNAME /usr/src/app

RUN pip --no-cache-dir install --find-links /wheels --no-index reporting-bot

USER $UNAME

CMD reporting-bot
