CURTIME=$(date +%Y-%m-%d-%H-%M) \
CLIENT="ngtcp2" \
CLIENT_PARAMS="--timeout=1000 -q --qlog-file=/logs/clientngtcp2_$CURTIME.qlog 193.167.100.100 4433 http://test/5000000" \
SERVER="ngtcp2" \
SERVER_PARAMS="--qlog-dir=/logs -q 193.167.100.100 4433 server.key server.crt" \
SCENARIO="simple-p2p --delay=15ms --bandwidth=5Mbps --queue=25" \
LOGDIR="$PWD/logs" \
CL_COMMIT="" \
SV_COMMIT="" \
docker-compose -f ../quic-network-simulator/docker-compose.yml up --abort-on-container-exit