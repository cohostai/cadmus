FROM python:2.7.15-alpine3.7
LABEL author=doankhoi@cohost.club

COPY requirements_x.txt /tmp/

RUN apk --no-cache add --virtual build-dependencies \
    build-base \
    gcc \
    g++ \
    libc-dev \
    libffi-dev \
    libxslt-dev \
    && pip install -r /tmp/requirements_x.txt \
    && rm -rf ~/.cache/pip \
    && apk del build-dependencies

RUN apk --no-cache add libxslt-dev

COPY requirements.txt /tmp/

RUN pip install -r /tmp/requirements.txt \
    && rm -rf ~/.cache/pip

COPY luckyluke /app/luckyluke/

WORKDIR /app

ENV PYTHONPATH=.

ENTRYPOINT ["python", "luckyluke/main.py"]
