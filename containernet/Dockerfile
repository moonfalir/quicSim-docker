FROM ubuntu:xenial

# install required packages
RUN apt-get clean
RUN apt-get update \
    && apt-get install -y  git \
    net-tools \
    aptitude \
    build-essential \
    python-setuptools \
    python-dev \
    python-pip \
    software-properties-common \
    ansible \
    curl \
    iptables \
    iputils-ping \
    sudo

# install containernet (using its Ansible playbook)
RUN git clone https://github.com/moonfalir/containernet
WORKDIR /containernet/ansible
RUN ansible-playbook -i "localhost," -c local --skip-tags "notindocker" install.yml
WORKDIR /containernet
RUN python setup.py develop

# Hotfix: https://github.com/pytest-dev/pytest/issues/4770
RUN pip2 install "more-itertools<=5.0.0"

# tell containernet that it runs in a container
ENV CONTAINERNET_NESTED 1

# Copy custom controllers to pox directory
RUN cp -a /containernet/poxcontrollers/. /pox/pox/forwarding/

COPY ./entrypoint.sh .
COPY ./scenarios/ ./scenarios/

# Important: This entrypoint is required to start the OVS service
ENTRYPOINT ["./entrypoint.sh"]
