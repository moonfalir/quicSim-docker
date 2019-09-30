CLIENT="quanttest" \
CLIENT_PARAMS="./bin/client -i client-eth0 -q /logs/clientmnquant.qlog http://10.0.0.251:4433/50000" \
SERVER="quanttest" \
SERVER_PARAMS="./bin/server -d ./ -i server-eth0 -q /logs/servermnquant.qlog" \
SCENARIO="--delay 15ms --bandwidth 10 --queue 25" \
LOGDIR="$PWD" \
docker-compose -f ../containernet/docker-compose.yml up