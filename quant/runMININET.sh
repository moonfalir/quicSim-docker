CURTIME=$(date +%Y-%m-%d-%H-%M) \
CLIENT="aioquic" \
CLIENT_PARAMS="--ca-certs tests/pycacert.pem --insecure -q /logs -l /logs/ssl-key.log --legacy-http https://10.0.0.251:4433/5000000" \
SERVER="quant" \
SERVER_PARAMS="-p 4433 -i eth1 -q /logs" \
SCENARIO="simple_p2p --delay 10ms --bandwidth 10 --queue 32" \
CLIENT_LOGS="$PWD/logs" \
SERVER_LOGS="$PWD/logs" \
CL_COMMIT="" \
SV_COMMIT="" \
docker-compose -f ../containernet/docker-compose.yml up