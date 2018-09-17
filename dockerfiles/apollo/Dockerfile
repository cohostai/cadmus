FROM python:2.7.15-alpine3.7
LABEL author=thuync@chongiadung.com

COPY requirements_x.txt /tmp/

RUN apk --no-cache add --virtual build-dependencies \
    build-base \
    gcc \
    g++ \
    libc-dev \
    libffi-dev \
    openssl-dev \
    && pip install -r /tmp/requirements_x.txt \
    && rm -rf ~/.cache/pip \
    && apk del build-dependencies

COPY requirements.txt /tmp/

RUN pip install -r /tmp/requirements.txt \
    && rm -rf ~/.cache/pip

COPY apollo /app/apollo/

WORKDIR /app/

# Should test using pypy
ENV PYTHONPATH=.
ENTRYPOINT ["python", "apollo/main.py"]

