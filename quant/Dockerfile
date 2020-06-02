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
 doxygen \
 graphviz \
 mercurial \
 pkg-config \
 net-tools \
 iputils-ping \
 iproute2 \
 python3 

#install latest version of cmake
RUN wget https://github.com/Kitware/CMake/releases/download/v3.16.4/cmake-3.16.4-Linux-x86_64.sh && chmod +x cmake-3.16.4-Linux-x86_64.sh && mkdir cmake

RUN ./cmake-3.16.4-Linux-x86_64.sh --skip-license --prefix=/cmake

# install quant
RUN git clone https://github.com/moonfalir/quant 

WORKDIR ./quant

RUN git submodule update --init --recursive

RUN mkdir Debug && mkdir ./Debug/external && mkdir ./Debug/external/lib

WORKDIR ./Debug

RUN /cmake/bin/cmake .. && make

COPY entrypoint_min.sh run_endpoint.sh updateAndBuild.sh tcp_server.py ./
RUN chmod +x entrypoint_min.sh run_endpoint.sh updateAndBuild.sh

ENTRYPOINT [ "./run_endpoint.sh" ]
