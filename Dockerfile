FROM python:rc-alpine

COPY ./app/requirements.txt ./

RUN apk add --no-cache --virtual .build-deps \
	build-base python3-dev linux-headers
RUN pip install --no-cache-dir -r requirements.txt
RUN apk del .build-deps
RUN apk add --no-cache libstdc++

COPY ./app ./app
COPY ./config.ini ./

ENTRYPOINT [ "python", "-m", "app" ]
