FROM python:rc-alpine

RUN apk add --virtual build-base python3-dev linux-headers

COPY ./app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apk del build-base python3-dev linux-headers

COPY ./app ./app
COPY ./config.ini ./

ENTRYPOINT [ "python", "-m", "app" ]
