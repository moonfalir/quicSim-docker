FROM quic-network-simulator-endpoint:latest

# download and build your QUIC implementation
RUN apt-get update && apt-get install -y \
 git \ 
 gcc-7 \ 
 g++ \  
 make \
 libev-dev \
 libssl-dev \
 libhttp-parser-dev \
 libbsd-dev \
 cmake \
 doxygen \
 graphviz \
 mercurial \
 pkg-config \
 net-tools \
 iputils-ping \
 iproute2

# install quant
RUN git clone https://github.com/NTAP/quant

WORKDIR ./quant

RUN git submodule update --init --recursive

RUN mkdir Debug && mkdir ./Debug/external && mkdir ./Debug/external/lib

WORKDIR ./Debug

RUN cmake .. && make

COPY entrypoint_min.sh .
RUN chmod +x entrypoint_min.sh

# copy run script and run it
COPY run_endpoint.sh .
RUN chmod +x run_endpoint.sh

ENTRYPOINT [ "./run_endpoint.sh" ]
