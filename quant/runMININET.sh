CURTIME=$(date +%Y-%m-%d-%H-%M) \
CLIENT="quant" \
CLIENT_PARAMS="-i eth1 -q /logs http://10.0.0.251:4433/5000000" \
SERVER="quant" \
SERVER_PARAMS="-t 2 -i eth1 -q /logs" \
SCENARIO="blackhole --delay 25ms --bandwidth 5 --queue 25 --on 6 --off 2" \
CLIENT_LOGS="$PWD/logs" \
SERVER_LOGS="$PWD/logs" \
CL_COMMIT="" \
SV_COMMIT="" \
docker-compose -f ../containernet/docker-compose.yml up