CURTIME=$(date +%Y-%m-%d-%H-%M) \
CLIENT="tcpebpf" \
CLIENT_PARAMS="iperf -c 10.0.0.251 5001" \
SERVER="tcpebpf" \
SERVER_PARAMS="iperf -s" \
SCENARIO="simple_p2p --delay 25ms --bandwidth 5 --queue 25" \
LOGDIR="$PWD" \
docker-compose -f ../containernet/docker-compose.yml up