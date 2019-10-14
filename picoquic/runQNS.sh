CURTIME=$(date +%Y-%m-%d-%H-%M) \
CLIENT="picoquic" \
CLIENT_PARAMS="-b /logs/clientpico_qns.log 192.168.100.100 4443" \
SERVER="picoquic" \
SERVER_PARAMS="-1 -b /logs/serverpico_qns.log" \
SCENARIO="simple-p2p --delay=25ms --bandwidth=1Mbps --queue=25" \
LOGDIR="../picoquic/logs" \
docker-compose -f ../quic-network-simulator/docker-compose.yml up #--abort-on-container-exit