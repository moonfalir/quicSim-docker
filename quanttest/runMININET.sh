CLIENT="quanttest" \
CLIENT_PARAMS="./bin/client -i client-eth0 http://10.0.0.251:4433/500000" \
SERVER="quanttest" \
SERVER_PARAMS="./bin/server -d ./ -i server-eth0" \
docker-compose -f ../containernet/docker-compose.yml up