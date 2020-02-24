FROM quic-network-simulator-endpoint:latest

# download and build your QUIC implementation
RUN apt-get update && apt-get install -y \
 git \ 
 gcc \ 
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
 iproute2 \
 python3 

# install quant
RUN git clone https://github.com/moonfalir/quant

WORKDIR ./quant

RUN git submodule update --init --recursive

RUN mkdir Debug && mkdir ./Debug/external && mkdir ./Debug/external/lib

WORKDIR ./Debug

RUN cmake .. && make

COPY entrypoint_min.sh run_endpoint.sh updateAndBuild.sh tcp_server.py ./
RUN chmod +x entrypoint_min.sh run_endpoint.sh updateAndBuild.sh

ENTRYPOINT [ "./run_endpoint.sh" ]
