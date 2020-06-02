CURTIME=$(date +%Y-%m-%d-%H-%M) \
CLIENT="aioquic" \
CLIENT_PARAMS="--ca-certs tests/pycacert.pem -q /logs/clientaioquic_$CURTIME.qlog -l /logs/ssl-key.log --legacy-http https://10.0.0.251:4433/5000000" \
SERVER="aioquic" \
SERVER_PARAMS="--certificate tests/ssl_cert.pem --private-key tests/ssl_key.pem -q /logs" \
SCENARIO="simple_p2p --delay 15ms --bandwidth 5 --queue 25" \
CLIENT_LOGS="$PWD/logs" \
SERVER_LOGS="$PWD/logs" \
CL_COMMIT="" \
SV_COMMIT="" \
docker-compose -f ../containernet/docker-compose.yml up