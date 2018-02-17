FROM python:3.6 as packages
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM python:3.6 as final
COPY --from=packages /usr/local/lib/python3.6/site-packages /usr/local/lib/python3.6/site-packages

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . .
RUN pip install .
