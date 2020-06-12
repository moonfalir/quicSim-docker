IMPLEMENTATIONS = {
    "quic_servers": [
        #{
        #    "name": "aioquic",
        #    "clpars_qns": "--ca-certs tests/pycacert.pem --insecure -q /logs/clientaioquic_$CURTIME.qlog --legacy-http https://193.167.100.100:4433/$BYTESREQ",
        #    "svpars_qns": "--certificate tests/ssl_cert.pem --private-key tests/ssl_key.pem --host 193.167.100.100 --port 4433 -q /logs",
        #    "clpars_min": "--ca-certs tests/pycacert.pem --insecure -q /logs/clientaioquic_$CURTIME.qlog --legacy-http https://10.0.0.251:4433/$BYTESREQ",
        #    "svpars_min": "--certificate tests/ssl_cert.pem --private-key tests/ssl_key.pem --port 4433 -q /logs",
        #    "clcommit": "",
        #    "svcommit": ""
        #},
        {
            "name": "quant",
            "clpars_qns": "-i eth0 -e 0xff000018 -q /logs/clientquant_$CURTIME.qlog http://193.167.100.100:4433/$BYTESREQ",
            "svpars_qns": "-t 1 -p 4433 -i eth0 -q /logs",
            "clpars_min": "-i eth1 -e 0xff000018 -q /logs/clientmnquant_$CURTIME.qlog http://10.0.0.251:4433/$BYTESREQ",
            "svpars_min": "-t 1 -p 4433 -i eth1 -q /logs",
            "clcommit": "",
            "svcommit": ""
        }
    ],
    "quic_clients": [
        {
            "name": "aioquic",
            "clpars_qns": "--ca-certs tests/pycacert.pem --insecure -q /logs -l /logs/ssl-key.log --legacy-http https://193.167.100.100:4433/$BYTESREQ",
            "clpars_min": "--ca-certs tests/pycacert.pem --insecure -q /logs -l /logs/ssl-key.log --legacy-http https://10.0.0.251:4433/$BYTESREQ",
            "clcommit": ""
        }
    ],
    "tcp_servers": [
        #{
        #    "name": "tcpebpf",
        #    "svpars_qns": "-c 193.167.0.100 -n $BYTESREQ --set-mss 1268",
        #    "svpars_min": "-c 10.0.0.252 -n $BYTESREQ --set-mss 1268",
        #    "svcommit": "tcp"
        #}
    ],
    "tcp_clients": [
        {
            "name": "tcpebpf",
            "clpars_qns": "-s",
            "clpars_min": "-s",
            "clcommit": "tcp"
        }
    ]
}