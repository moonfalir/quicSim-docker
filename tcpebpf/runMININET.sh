CURTIME=$(date +%Y-%m-%d-%H-%M) \
CLIENT="tcpebpf" \
CLIENT_PARAMS="./run_min_client.sh" \
SERVER="tcpebpf" \
SERVER_PARAMS="./run_min_server.sh" \
SCENARIO="blackhole --delay 15ms --bandwidth 5 --queue 25 --on 6 --off 2 -k" \
LOGDIR="$PWD" \
docker-compose -f ../containernet/docker-compose.yml up