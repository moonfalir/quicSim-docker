FROM quic-network-simulator-endpoint:latest

# download and build your QUIC implementation
RUN apt-get update && apt-get install -y \
 git \
 libssl-dev \
 python3-pip \
 python3-dev \
 net-tools \
 iputils-ping \
 iproute2

# install aioquic
RUN git clone https://github.com/aiortc/aioquic

WORKDIR /aioquic

RUN pip3 install -e . && pip3 install aiofiles asgiref httpbin starlette wsproto

COPY entrypoint_min.sh .
RUN chmod +x entrypoint_min.sh

# copy run base script and run it
COPY run_endpoint.sh .
RUN chmod +x run_endpoint.sh

ENTRYPOINT [ "./run_endpoint.sh" ]
