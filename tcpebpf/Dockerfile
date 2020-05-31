FROM quic-network-simulator-endpoint:latest

#Add debian linux headers
RUN apt-get update && apt-get install -y gnupg

RUN echo deb http://deb.debian.org/debian buster-backports main contrib non-free | tee /etc/apt/sources.list.d/buster-backports.list && \
 apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 04EE7237B7D453EC && apt-get update

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
 iproute2 \
 iperf3

RUN git clone https://github.com/iovisor/bcc && mkdir bcc/build

WORKDIR /bcc/build

RUN cmake .. -DCMAKE_INSTALL_PREFIX=/usr && make && make install

COPY bccscripts /bccscripts

COPY tcp_server.py captureAndServe.py ./

COPY entrypoint_min.sh run_endpoint.sh updateAndBuild.sh ./
RUN chmod +x entrypoint_min.sh run_endpoint.sh updateAndBuild.sh

ENTRYPOINT [ "./run_endpoint.sh" ]