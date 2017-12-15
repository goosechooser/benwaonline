FROM python:3.6

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir requirements.txt
