FROM quic-network-simulator-endpoint:latest

# download and build your QUIC implementation
RUN apt-get update && apt-get install -y \
 git \
 make \
 pkg-config \
 cmake \
 perl \
 libtest-tcp-perl \
 libscope-guard-perl \
 net-tools \
 iputils-ping \
 iproute2

# install openssl
RUN git clone https://github.com/openssl/openssl

WORKDIR /openssl

RUN ./config enable-tls1_3 && make && make test && make install

WORKDIR /

# install picotls
RUN git clone https://github.com/h2o/picotls

WORKDIR /picotls

RUN git submodule init && git submodule update

COPY CMakeLists.txt /picotls

RUN cmake . && make && make check

WORKDIR /

# install picoquic
RUN git clone https://github.com/private-octopus/picoquic

WORKDIR /picoquic

RUN cmake . && make
# copy run script and run it
COPY run_endpoint.sh .
RUN chmod +x run_endpoint.sh

ENTRYPOINT [ "./run_endpoint.sh" ]
