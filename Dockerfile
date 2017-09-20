FROM goosechooser/flask_base

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir . 
