FROM python:2.7.15-alpine3.7
LABEL author=thuync@chongiadung.com

COPY requirements.txt /tmp/

RUN pip install -r /tmp/requirements.txt \
    && rm -rf ~/.cache/pip

COPY athena /app/athena/

WORKDIR /app/

# Should test using pypy
ENV PYTHONPATH=.
ENTRYPOINT ["python", "athena/main.py"]

