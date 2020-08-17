CURTIME=$(date +%Y-%m-%d-%H-%M) \
CLIENT="tcpebpf" \
CLIENT_PARAMS="-s" \
SERVER="tcpebpf" \
SERVER_PARAMS="-c 10.0.0.252 -n 5000000 --set-mss 1268" \
SCENARIO="simple_p2p --delay 15ms --bandwidth 5 --queue 25 -k" \
CLIENT_LOGS="$PWD/logs" \
SERVER_LOGS="$PWD/logs" \
CL_COMMIT="" \
SV_COMMIT="" \
docker-compose -f ../containernet/docker-compose.yml up