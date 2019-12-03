IMPLEMENTATIONS = [
    {
        "name": "aioquic",
        "clpars_qns": "",
        "svpars_qns": "",
        "clpars_min": "",
        "svpars_min": "",
        "clcommit": "",
        "svcommit": ""
    },
    {
        "name": "ngtcp2",
        "clpars_qns": "--timeout=1000 -q --qlog-file=/logs/clientngtcp2_$CURTIME.qlog 193.167.100.100 4433 http://server/$BYTESREQ",
        "svpars_qns": "--qlog-dir=/logs -q 193.167.100.100 4433 server.key server.crt",
        "clpars_min": "--timeout=1000 -q --qlog-file=/logs/clientmnngtcp2_$CURTIME.qlog 10.0.0.251 4433 http://server/$BYTESREQ",
        "svpars_min": "--qlog-dir=/logs -q 10.0.0.251 4433 server.key server.crt",
        "clcommit": "",
        "svcommit": ""
    },
    {
        "name": "picoquic",
        "clpars_qns": "",
        "svpars_qns": "",
        "clpars_min": "",
        "svpars_min": "",
        "clcommit": "",
        "svcommit": ""
    },
    {
        "name": "quant",
        "clpars_qns": "-i eth0 -q /logs/clientquant_$CURTIME.qlog http://193.167.100.100:4433/$BYTESREQ",
        "svpars_qns": "-d ./ -i eth0 -q /logs/serverquant_$CURTIME.qlog",
        "clpars_min": "-i eth1 -q /logs/clientmnquant_$CURTIME.qlog http://10.0.0.251:4433/$BYTESREQ",
        "svpars_min": "-t 2 -i eth1 -q /logs/servermnquant_$CURTIME.qlog",
        "clcommit": "",
        "svcommit": ""
    },
]