FROM python:3.9-alpine

#[1/2]本地调试默认源太慢，使用清华源，调试时可以取消注释。
#RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories

#[2/2]本地调试Pip默认源太慢，使用清华源，调试时可以取消注释。
#RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U
#RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

COPY ./app/requirements.txt ./
RUN apk add --no-cache --virtual .build-deps \
	build-base python3-dev git linux-headers \
	libressl-dev musl-dev libffi-dev cargo && \
pip install --no-cache-dir -r requirements.txt && \
python -m pip install 'requests[socks]' && \
apk add --no-cache protoc && \
pip install setuptools-rust && \
git clone --depth=1 https://github.com/NoMore201/googleplay-api && \
cd ./googleplay-api && python setup.py build && python setup.py install && \
pip uninstall -y setuptools-rust semantic_version toml && \
rm -rf ./googleplay-api && \
apk del .build-deps && \
apk add --no-cache libstdc++ libressl-dev

COPY ./app ./app
COPY ./config.ini ./

ENTRYPOINT [ "python", "-m", "app" ]
