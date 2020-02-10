IMPLEMENTATIONS = {
    "servers": [
        {
            "name": "aioquic",
            "clpars_qns": "--ca-certs tests/pycacert.pem --insecure -q /logs/clientaioquic_$CURTIME.qlog --legacy-http https://193.167.100.100:4433/$BYTESREQ",
            "svpars_qns": "--certificate tests/ssl_cert.pem --private-key tests/ssl_key.pem --host 193.167.100.100 --port 4433 -q /logs",
            "clpars_min": "--ca-certs tests/pycacert.pem --insecure -q /logs/clientaioquic_$CURTIME.qlog --legacy-http https://10.0.0.251:4433/$BYTESREQ",
            "svpars_min": "--certificate tests/ssl_cert.pem --private-key tests/ssl_key.pem --port 4433 -q /logs",
            "clcommit": "",
            "svcommit": ""
        },
        #{
        #    "name": "ngtcp2",
        #    "clpars_qns": "--timeout=1000 -q --qlog-file=/logs/clientngtcp2_$CURTIME.qlog 193.167.100.100 4433 http://server/$BYTESREQ",
        #    "svpars_qns": "--qlog-dir=/logs -q 193.167.100.100 4433 server.key server.crt",
        #    "clpars_min": "--timeout=1000 -q --qlog-file=/logs/clientmnngtcp2_$CURTIME.qlog 10.0.0.251 4433 http://server/$BYTESREQ",
        #    "svpars_min": "--qlog-dir=/logs -q 10.0.0.251 4433 server.key server.crt",
        #    "clcommit": "",
        #    "svcommit": ""
        #},
        {
            "name": "picoquic",
            "clpars_qns": "-L -a hq-24 -b /logs/clientpico_qns.log 193.167.100.100 4433 0:/$BYTESREQ;",
            "svpars_qns": "-1 -L -p 4433 -b /logs/serverpico_qns.log",
            "clpars_min": "-L -a hq-24 -b /logs/clientpico_mn.log 10.0.0.251 4433 0:/$BYTESREQ;",
            "svpars_min": "-1 -L -p 4433 -b /logs/serverpico_mn.log",
            "clcommit": "",
            "svcommit": ""
        },
        {
            "name": "quant",
            "clpars_qns": "-i eth0 -e 0xff000018 -q /logs/clientquant_$CURTIME.qlog http://193.167.100.100:4433/$BYTESREQ",
            "svpars_qns": "-d ./ -p 4433 -i eth0 -q /logs/serverquant_$CURTIME.qlog",
            "clpars_min": "-i eth1 -e 0xff000018 -q /logs/clientmnquant_$CURTIME.qlog http://10.0.0.251:4433/$BYTESREQ",
            "svpars_min": "-t 2 -p 4433 -i eth1 -q /logs/servermnquant_$CURTIME.qlog",
            "clcommit": "",
            "svcommit": ""
        }
    ],
    "clients": [
        {
            "name": "aioquic",
            "clpars_qns": "--ca-certs tests/pycacert.pem --insecure -q /logs/clientaioquic_$CURTIME.qlog -l /logs/ssl-key.log --legacy-http https://193.167.100.100:4433/$BYTESREQ",
            "clpars_min": "--ca-certs tests/pycacert.pem --insecure -q /logs/clientaioquic_$CURTIME.qlog -l /logs/ssl-key.log --legacy-http https://10.0.0.251:4433/$BYTESREQ",
            "clcommit": ""
        }
    ]
}