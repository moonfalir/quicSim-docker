CURTIME=$(date +%Y-%m-%d-%H-%M) \
CLIENT="quant" \
CLIENT_PARAMS="-i eth0 -q /logs/clientquant_$CURTIME.qlog http://193.167.100.100:4433/5000000" \
SERVER="quant" \
SERVER_PARAMS="-d ./ -i eth0 -q /logs/serverquant_$CURTIME.qlog" \
SCENARIO="simple-p2p --delay=15ms --bandwidth=10Mbps --queue=25" \
LOGDIR="$PWD/logs" \
docker-compose -f ../quic-network-simulator/docker-compose.yml up --abort-on-container-exit