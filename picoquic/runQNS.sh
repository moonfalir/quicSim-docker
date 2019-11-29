CURTIME=$(date +%Y-%m-%d-%H-%M) \
CLIENT="picoquic" \
CLIENT_PARAMS="-L -b /logs/clientpico_qns.log 193.167.100.100 4443 0:/5000000;" \
SERVER="picoquic" \
SERVER_PARAMS="-1 -L -b /logs/serverpico_qns.log" \
SCENARIO="simple-p2p --delay=25ms --bandwidth=5Mbps --queue=25" \
LOGDIR="../picoquic/logs" \
docker-compose -f ../quic-network-simulator/docker-compose.yml up --abort-on-container-exit