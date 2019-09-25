CLIENT="quanttest" \
CLIENT_PARAMS="-i eth0 -q /logs/clientquant.qlog http://192.168.100.100:4433/50000" \
SERVER="quanttest" \
SERVER_PARAMS="-d ./ -i eth0 -q /logs/serverquant.qlog" \
SCENARIO="droplist --delay=15ms --bandwidth=10Mbps --queue=25 --drops_to_client=1,3,4 --drops_to_server=5" \
docker-compose -f ../quic-network-simulator/docker-compose.yml up