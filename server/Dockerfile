FROM python:3.8-alpine

COPY ./app/requirements.txt ./

#[1/2]本地调试默认源太慢，使用清华源，调试时可以取消注释。
#RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories


RUN apk add --no-cache --virtual .build-deps \
	build-base python3-dev git linux-headers \
 	libressl-dev musl-dev libffi-dev


#[2/2]本地调试Pip默认源太慢，使用清华源，调试时可以取消注释。
#RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U
#RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple


RUN pip install --no-cache-dir -r requirements.txt
RUN python -m pip install 'requests[socks]'

RUN apk add --no-cache protoc
RUN git clone --depth=1 https://github.com/NoMore201/googleplay-api
RUN cd ./googleplay-api && python setup.py build && python setup.py install
RUN rm -rf ./googleplay-api

RUN apk del .build-deps
RUN apk add --no-cache libstdc++

COPY ./app ./app
COPY ./config.ini ./

ENTRYPOINT [ "python", "-m", "app" ]
