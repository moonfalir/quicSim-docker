FROM quic-network-simulator-endpoint:latest

RUN apt-get update && apt-get install -y \
 git \
 python-dev \
 python3 \
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

COPY simple_socket /simple_socket

COPY tcp_server.py .

COPY entrypoint_min.sh run_endpoint.sh ./
RUN chmod +x entrypoint_min.sh run_endpoint.sh

ENTRYPOINT [ "./run_endpoint.sh" ]