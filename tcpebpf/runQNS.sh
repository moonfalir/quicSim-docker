CURTIME=$(date +%Y-%m-%d-%H-%M) \
CLIENT="tcpebpf" \
CLIENT_PARAMS="-s" \
SERVER="tcpebpf" \
SERVER_PARAMS="-c 193.167.0.100 -n 5000000 --set-mss 1268" \
SCENARIO="simple-p2p --delay=15ms --bandwidth=5Mbps --queue=25" \
CLIENT_LOGS="$PWD/logs" \
SERVER_LOGS="$PWD/logs" \
CL_COMMIT="" \
SV_COMMIT="" \
docker-compose -f ../quic-network-simulator/docker-compose.yml -f ../quic-network-simulator/docker-compose.tcp.yml up --abort-on-container-exit