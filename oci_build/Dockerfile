FROM python:3.10-slim

#[1/2]本地调试默认源太慢，使用科大源，调试时可以取消注释。
#RUN sed -i 's#deb.debian.org#mirrors.ustc.edu.cn#g' /etc/apt/sources.list

#[2/2]本地调试Pip默认源太慢，使用清华源，调试时可以取消注释。
#RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U
#RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

COPY ./server/requirements.txt ./
COPY ./oci_build/DockerfileRUN.sh ./
RUN ./DockerfileRUN.sh && rm ./DockerfileRUN.sh
COPY ./scripts/boot.sh ./
COPY ./server/config.py ./
COPY ./server/utils ./utils
COPY ./server/database ./database
COPY ./server/hello ./hello
COPY ./server/proxy ./proxy
COPY ./server/getter ./getter

ENTRYPOINT [ "bash", "./boot.sh" ]
