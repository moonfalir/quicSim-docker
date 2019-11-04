CURTIME=$(date +%Y-%m-%d-%H-%M) \
CLIENT="tcpebpf" \
CLIENT_PARAMS="" \
SERVER="tcpebpf" \
SERVER_PARAMS="" \
SCENARIO="simple-p2p --delay=15ms --bandwidth=5Mbps --queue=25" \
LOGDIR="$PWD/logs" \
docker-compose -f ../quic-network-simulator/docker-compose.yml up --abort-on-container-exit