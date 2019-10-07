CURTIME=$(date +%Y-%m-%d-%H-%M) \
CLIENT="aioquic" \
CLIENT_PARAMS="--ca-certs tests/pycacert.pem -q /logs/clientaioquic_$CURTIME.qlog --legacy-http https://192.168.100.100:4433/50000" \
SERVER="aioquic" \
SERVER_PARAMS="--certificate tests/ssl_cert.pem --private-key tests/ssl_key.pem --host 192.168.100.100 -q /logs" \
SCENARIO="simple-p2p --delay=15ms --bandwidth=10Mbps --queue=25" \
docker-compose -f ../quic-network-simulator/docker-compose.yml up