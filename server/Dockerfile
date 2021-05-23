FROM python:3.9-alpine

#[1/2]本地调试默认源太慢，使用清华源，调试时可以取消注释。
#RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories

#[2/2]本地调试Pip默认源太慢，使用清华源，调试时可以取消注释。
#RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U
#RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

COPY ./app/requirements.txt ./
COPY ./DockerfileRUN.sh ./
RUN ./DockerfileRUN.sh && rm ./DockerfileRUN.sh
COPY ./app ./app
COPY ./config.ini ./

ENTRYPOINT [ "python", "-m", "app" ]
