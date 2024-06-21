FROM python:3.11-alpine
LABEL author=thuync@chongiadung.com

WORKDIR /app/

RUN apk update && apk --no-cache add \
    build-base \
    gcc \
    g++ \
    libc-dev \
    libffi-dev \
    mariadb-dev \
    libxslt-dev \
    linux-headers

COPY Pipfile Pipfile.lock ./
RUN pip3 install --upgrade pip
RUN pip3 install pipenv
RUN pipenv install --system --deploy

COPY cadmus /app/cadmus/

ENTRYPOINT ["gunicorn", "cadmus", "-b", "0.0.0.0:7111", "-w", "3", "-k", "gevent", "--name", "cadmus", "--timeout", "120"]
