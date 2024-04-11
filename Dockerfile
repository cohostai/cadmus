FROM python:3.11-alpine
LABEL author=thuync@chongiadung.com

RUN apk --no-cache add --virtual build-dependencies \
    build-base \
    gcc \
    g++ \
    && apk del build-dependencies

COPY Pipfile Pipfile.lock /app/cadmus/
RUN pip3 install --upgrade pip
RUN pip3 install pipenv
RUN pipenv install && rm -rf ~/.cache/pip

COPY cadmus /app/cadmus/

WORKDIR /app/

ENTRYPOINT ["gunicorn", "cadmus", "-b", "0.0.0.0:7111", "-w", "3", "-k", "gevent", "--name", "cadmus", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]
