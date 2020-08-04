FROM python:rc-alpine

ENV CC=clang
ENV CXX=clang++

RUN apk --virtual --no-cache --update add build-base clang python3-dev linux-headers

COPY ./app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apk del build-base clang python3-dev linux-headers

COPY ./app ./app
COPY ./config.ini ./

ENTRYPOINT [ "python", "-m", "app" ]
