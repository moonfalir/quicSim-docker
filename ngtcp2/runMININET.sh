CURTIME=$(date +%Y-%m-%d-%H-%M) \
CLIENT="ngtcp2" \
CLIENT_PARAMS="--timeout=1000 -q --qlog-file=/logs/clientmnngtcp2_$CURTIME.qlog 10.0.0.251 4433 http://server/5000000" \
SERVER="ngtcp2" \
SERVER_PARAMS="--qlog-dir=/logs -q 10.0.0.251 4433 server.key server.crt" \
SCENARIO="simple_p2p --delay=15ms --bandwidth=5 --queue=25" \
LOGDIR="$PWD" \
docker-compose -f ../containernet/docker-compose.yml up