FROM quic-network-simulator-endpoint:latest

# download and build your QUIC implementation
RUN apt-get update && apt-get install -y \
 git \ 
 gcc-7 \ 
 g++ \  
 make \
 libev-dev \
 pkg-config \
 autoconf \
 automake \
 autotools-dev \
 libtool \
 libcunit1 \
 net-tools \
 iputils-ping \
 iproute2 \
 python3

# install patched openssl
RUN git clone --depth 1 -b OpenSSL_1_1_1d-quic-draft-24 https://github.com/tatsuhiro-t/openssl

WORKDIR /openssl

RUN ./config enable-tls1_3 --prefix=$PWD/build && make -j$(nproc) && make install_sw

WORKDIR /

# install nghttp3
RUN git clone https://github.com/ngtcp2/nghttp3

WORKDIR /nghttp3

RUN autoreconf -i && ./configure --prefix=$PWD/build --enable-lib-only && make -j$(nproc) check && make install

WORKDIR /

#install ngtcp2
RUN git clone https://github.com/ngtcp2/ngtcp2

WORKDIR /ngtcp2

RUN autoreconf -i && ./configure PKG_CONFIG_PATH=$PWD/../openssl/build/lib/pkgconfig:$PWD/../nghttp3/build/lib/pkgconfig \
 LDFLAGS="-Wl,-rpath,$PWD/../openssl/build/lib" && make -j$(nproc) check


COPY server.crt server.key ./

COPY entrypoint_min.sh run_endpoint.sh updateAndBuild.sh tcp_server.py ./
RUN chmod +x entrypoint_min.sh run_endpoint.sh updateAndBuild.sh

ENTRYPOINT [ "./run_endpoint.sh" ]
