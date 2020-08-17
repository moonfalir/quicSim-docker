FROM ubuntu:18.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    libglib2.0 \
    python3 \
    gcc \ 
    g++ \
    cmake \
    make \
    wget \
    libgcrypt20-dev \
    git \
    libc-ares-dev \
    flex \
    bison \
    unzip

RUN mkdir wiresharksrc && mkdir wiresharkbld

WORKDIR /wiresharksrc

RUN wget https://github.com/wireshark/wireshark/archive/151ee605559ac0d61eb8618a75985772c57dbfa8.zip &&  unzip 151ee605559ac0d61eb8618a75985772c57dbfa8.zip

WORKDIR /wiresharkbld

RUN cmake -DBUILD_wireshark=OFF -DBUILD_mergecap=OFF -DBUILD_dftest=OFF -DBUILD_randpkt=OFF -DBUILD_dumpcap=OFF -DBUILD_rawshark=OFF -DENABLE_PCAP=OFF -DENABLE_PLUGINS=OFF /wiresharksrc/wireshark-151ee605559ac0d61eb8618a75985772c57dbfa8

RUN make

COPY convert.py .

ENTRYPOINT [ "python3", "convert.py" ]