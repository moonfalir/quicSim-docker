CLIENT="quanttest" \
CLIENT_PARAMS="-i eth0 -q /logs/clientquant.log http://192.168.100.100:4433/500000" \
SERVER="quanttest" \
SERVER_PARAMS="-d ./ -i eth0 -q /logs/serverquant.log" \
SCENARIO="simple-p2p --delay=15ms --bandwidth=10Mbps --queue=25" \
docker-compose -f ../quic-network-simulator/docker-compose.yml up