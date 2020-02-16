CURTIME=$(date +%Y-%m-%d-%H-%M) \
CLIENT="tcpebpf" \
CLIENT_PARAMS="--ip 10.0.0.251 --port 8080 --bytes 5000000" \
SERVER="tcpebpf" \
SERVER_PARAMS="--port 8080" \
SCENARIO="simple_p2p --delay 15ms --bandwidth 5 --queue 25 -k" \
CLIENT_LOGS="$PWD/logs" \
SERVER_LOGS="$PWD/logs" \
CL_COMMIT="" \
SV_COMMIT="" \
docker-compose -f ../containernet/docker-compose.yml up