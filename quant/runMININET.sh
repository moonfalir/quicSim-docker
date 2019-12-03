CURTIME=$(date +%Y-%m-%d-%H-%M) \
CLIENT="quant" \
CLIENT_PARAMS="-i eth1 -q /logs/clientmnquant_$CURTIME.qlog http://10.0.0.251:4433/5000000" \
SERVER="quant" \
SERVER_PARAMS="-t 2 -i eth1 -q /logs/servermnquant_$CURTIME.qlog" \
SCENARIO="simple_p2p --delay 25ms --bandwidth 5 --queue 25" \
LOGDIR="$PWD" \
CL_COMMIT="" \
SV_COMMIT="" \
docker-compose -f ../containernet/docker-compose.yml up