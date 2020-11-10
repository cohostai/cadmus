FROM python:2.7.15-alpine3.7
LABEL author=thuync@chongiadung.com

COPY requirements_x.txt /tmp/

RUN apk --no-cache add --virtual build-dependencies \
    build-base \
    gcc \
    g++ \
    && pip install -r /tmp/requirements_x.txt \
    && rm -rf ~/.cache/pip \
    && apk del build-dependencies

COPY requirements.txt /tmp/

RUN pip install -r /tmp/requirements.txt \
    && rm -rf ~/.cache/pip

COPY cadmus /app/cadmus/

WORKDIR /app/

ENTRYPOINT ["gunicorn", "cadmus", "-b", "0.0.0.0:7111", "-w", "3", "-k", "gevent", "--name", "cadmus", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]
