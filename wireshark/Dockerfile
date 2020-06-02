FROM ubuntu:18.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    libglib2.0 \
    python3 \
    gcc \ 
    g++ \
    cmake \
    make \
    wget \
    libgcrypt20-dev \
    git \
    libc-ares-dev \
    flex \
    bison

RUN mkdir wiresharksrc && mkdir wiresharkbld

WORKDIR /wiresharksrc

RUN wget https://www.wireshark.org/download/automated/src/wireshark-3.3.0rc0-1315-ge0eefe186af4.tar.xz &&  tar -xvf wireshark-3.3.0rc0-1315-ge0eefe186af4.tar.xz

WORKDIR /wiresharkbld

RUN cmake -DBUILD_wireshark=OFF -DENABLE_CAP=OFF -DENABLE_ZLIB=OFF /wiresharksrc/wireshark-3.3.0rc0-1315-ge0eefe186af4

RUN make

COPY convert.py .

ENTRYPOINT [ "python3", "convert.py" ]