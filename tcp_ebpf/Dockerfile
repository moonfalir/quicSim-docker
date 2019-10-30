FROM quic-network-simulator-endpoint:latest

RUN apt-get update && apt-get install -y \
 git \
 python-dev \
 linux-headers-$(uname -r) \
 clang \
 cmake \
 gcc \
 flex \
 bison \
 luajit \
 build-essential \
 libedit-dev \
 zlib1g-dev \
 libelf-dev \
 libclang-dev \
 iperf \
 tcpdump \
 net-tools \
 iputils-ping \
 iproute2

RUN git clone https://github.com/iovisor/bcc && mkdir bcc/build

WORKDIR /bcc/build

RUN cmake .. -DCMAKE_INSTALL_PREFIX=/usr && make && make install

COPY bccscripts /bccscripts