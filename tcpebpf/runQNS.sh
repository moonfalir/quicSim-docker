CURTIME=$(date +%Y-%m-%d-%H-%M) \
CLIENT="tcpebpf" \
CLIENT_PARAMS="--ip 193.167.100.100 --port 8080 --bytes 5000000" \
SERVER="tcpebpf" \
SERVER_PARAMS="--port 8080" \
SCENARIO="simple-p2p --delay=15ms --bandwidth=5Mbps --queue=25" \
LOGDIR="$PWD/logs" \
docker-compose -f ../quic-network-simulator/docker-compose.yml -f ../quic-network-simulator/docker-compose.tcp.yml up --abort-on-container-exit