FROM python:2.7.15-alpine3.7
LABEL author=doankhoi@cohost.club

RUN pip install -r /tmp/requirements.txt \
    && rm -rf ~/.cache/pip

COPY luckyluke /app/luckyluke/

WORKDIR /app

ENTRYPOINT ["python", "luckyluke/slack_rtm/rtm.py "]
