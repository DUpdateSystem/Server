FROM python:rc-alpine

COPY ./app/requirements.txt ./

#[1/2]本地调试默认源太慢,使用清华源,部署时建议注释.
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories


RUN apk add --no-cache --virtual .build-deps \
	build-base python3-dev linux-headers


#[2/2]本地调试Pip默认源太慢,使用清华源,部署时建议注释.
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple


RUN pip install --no-cache-dir -r requirements.txt
RUN apk del .build-deps
RUN apk add --no-cache libstdc++

COPY ./app ./app
COPY ./config.ini ./

ENTRYPOINT [ "python", "-m", "app" ]
