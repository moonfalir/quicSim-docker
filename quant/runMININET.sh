CURTIME=$(date +%Y-%m-%d-%H-%M) \
CLIENT="quant" \
CLIENT_PARAMS="./bin/client -i client-eth0 -q /logs/clientmnquant_$CURTIME.qlog http://10.0.0.251:4433/500000" \
SERVER="quant" \
SERVER_PARAMS="./bin/server -d ./ -i server-eth0 -q /logs/servermnquant_$CURTIME.qlog" \
SCENARIO="blackhole --delay 50ms --bandwidth 1 --queue 25 --on 1 --off 2 --repeat 2" \
LOGDIR="$PWD" \
docker-compose -f ../containernet/docker-compose.yml up