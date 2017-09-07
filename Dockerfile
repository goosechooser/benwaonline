FROM python:alpine3.6

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=benwaonline

CMD ["flask", "initdb"]
CMD ["flask", "run"]
