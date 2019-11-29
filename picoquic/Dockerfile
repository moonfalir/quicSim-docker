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
 iproute2 \
 libssl-dev

## install picotls
RUN git clone https://github.com/h2o/picotls

WORKDIR /picotls

RUN git submodule init && git submodule update

#COPY CMakeLists.txt /picotls

RUN cmake . && make && make check

WORKDIR /

# install picoquic
RUN git clone https://github.com/private-octopus/picoquic

WORKDIR /picoquic

RUN cmake . && make

COPY entrypoint_min.sh .
RUN chmod +x entrypoint_min.sh
# copy run script and run it
COPY run_endpoint.sh .
RUN chmod +x run_endpoint.sh

ENTRYPOINT [ "./run_endpoint.sh" ]
