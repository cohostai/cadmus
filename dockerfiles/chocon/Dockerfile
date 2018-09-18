FROM python:2.7.15-alpine3.7
LABEL author=thuync@chongiadung.com

COPY requirements_x.txt /tmp/

RUN apk --no-cache add --virtual build-dependencies \
    build-base \
    gcc \
    g++ \
    libc-dev \
    libffi-dev \
    mariadb-dev \
    py-mysqldb \
    libxslt-dev \
    && pip install -r /tmp/requirements_x.txt \
    && rm -rf ~/.cache/pip \
    && apk del build-dependencies

COPY requirements.txt /tmp/

RUN pip install -r /tmp/requirements.txt \
    && rm -rf ~/.cache/pip

COPY chocon /app/chocon/

WORKDIR /app/

ENTRYPOINT ["gunicorn", "chocon.api", "-b", "0.0.0.0:6111", "-w", "3", "-k", "gevent", "--name", "chocon-apis", "--log-file", "-"]
