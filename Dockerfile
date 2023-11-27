FROM ubuntu:20.04

ARG FLASK_PORT
ARG GRPC_PORT

ENV DEBIAN_FRONTEND=noninteractive

RUN # 更新apt包列表
RUN apt-get update

# 安装必要的依赖工具
RUN apt-get install -y \
    build-essential \
    wget \
    libffi-dev \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libffi-dev \
    liblzma-dev

# 下载并编译Python 3.11
WORKDIR /tmp
RUN wget https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tgz
RUN tar xvf Python-3.11.0.tgz
WORKDIR /tmp/Python-3.11.0
RUN ./configure --enable-optimizations
RUN make -j$(nproc)
RUN make altinstall

# 更新update-alternatives，将python3链接指向新安装的Python 3.11
RUN update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.11 1

# 安装pip
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3.11 get-pip.py

# 清理临时文件
WORKDIR /
RUN rm -rf /tmp/Python-3.11.0
RUN rm -f /tmp/Python-3.11.0.tgz
RUN rm -f get-pip.py

WORKDIR /app
COPY . /app

RUN pip install -r /app/requirements.txt

CMD ["python3","server.py"]
