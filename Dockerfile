FROM python:3.8-slim-buster AS builder

RUN mkdir -p /app
RUN apt-get update && apt-get install -y git gcc clang cmake g++ pkg-config python3-dev wget libpq-dev

WORKDIR /app
RUN wget https://gitlab.matrix.org/matrix-org/olm/-/archive/master/olm-master.tar.bz2 \
    && tar -xvf olm-master.tar.bz2 \
    && cd olm-master && make && make PREFIX="/usr" install

RUN pip --no-cache-dir install --upgrade pip setuptools wheel

COPY . /app

RUN pip wheel . --wheel-dir /wheels --find-links /wheels


#
FROM python:3.8-slim-buster

COPY --from=builder /usr/lib/libolm* /usr/lib/
COPY --from=builder /wheels /wheels
RUN apt-get update && apt-get install -y libpq-dev && apt-get clean

WORKDIR /usr/src/app

RUN pip --no-cache-dir install --find-links /wheels --no-index reporting-bot


CMD reporting-bot
