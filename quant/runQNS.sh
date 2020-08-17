CURTIME=$(date +%Y-%m-%d-%H-%M) \
CLIENT="aioquic" \
CLIENT_PARAMS="--ca-certs tests/pycacert.pem --insecure -q /logs -l /logs/ssl-key.log --legacy-http https://193.167.100.100:4433/5000000" \
SERVER="quant" \
SERVER_PARAMS="-p 4433 -i eth0 -q /logs" \
SCENARIO="simple-p2p --delay=10ms --bandwidth=10Mbps --queue=32" \
CLIENT_LOGS="$PWD/logs" \
SERVER_LOGS="$PWD/logs" \
CL_COMMIT="" \
SV_COMMIT="" \
docker-compose -f ../quic-network-simulator/docker-compose.yml up --abort-on-container-exit