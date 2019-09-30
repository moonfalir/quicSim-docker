CURTIME=$(date +%Y-%m-%d-%H-%M) \
CLIENT="quant" \
CLIENT_PARAMS="./bin/client -i client-eth0 -q /logs/clientmnquant_$CURTIME.qlog http://10.0.0.251:4433/50000" \
SERVER="quant" \
SERVER_PARAMS="./bin/server -d ./ -i server-eth0 -q /logs/servermnquant_$CURTIME.qlog" \
SCENARIO="simple_p2p --delay 15ms --bandwidth 10 --queue 25" \
LOGDIR="$PWD" \
docker-compose -f ../containernet/docker-compose.yml up