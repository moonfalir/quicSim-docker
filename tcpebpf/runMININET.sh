CURTIME=$(date +%Y-%m-%d-%H-%M) \
CLIENT="tcpebpf" \
CLIENT_PARAMS="" \
SERVER="tcpebpf" \
SERVER_PARAMS="" \
SCENARIO="simple_p2p --delay 15ms --bandwidth 5 --queue 25 -k" \
CLIENT_LOGS="$PWD/logs" \
SERVER_LOGS="$PWD/logs" \
CL_COMMIT="" \
SV_COMMIT="" \
docker-compose -f ../containernet/docker-compose.yml up