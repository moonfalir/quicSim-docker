SCENARIOS = [
    {
        "name": "dl5_bw5_q2",
        "bytesreq": "5000000",
        "qns": "simple-p2p --delay=5ms --bandwidth=5Mbps --queue=2",
        "min": "simple_p2p --delay 5ms --bandwidth 5 --queue 2"
    },
    {
        "name": "dl10_bw5_q5",
        "bytesreq": "5000000",
        "qns": "simple-p2p --delay=10ms --bandwidth=5Mbps --queue=5",
        "min": "simple_p2p --delay 10ms --bandwidth 5 --queue 5"
    },
    {
        "name": "dl25_bw5_q12",
        "bytesreq": "5000000",
        "qns": "simple-p2p --delay=25ms --bandwidth=5Mbps --queue=12",
        "min": "simple_p2p --delay 25ms --bandwidth 5 --queue 12"
    },
    {
        "name": "dl5_bw10_q5",
        "bytesreq": "5000000",
        "qns": "simple-p2p --delay=5ms --bandwidth=10Mbps --queue=5",
        "min": "simple_p2p --delay 5ms --bandwidth 10 --queue 5"
    },
    {
        "name": "dl10_bw10_q10",
        "bytesreq": "5000000",
        "qns": "simple-p2p --delay=10ms --bandwidth=10Mbps --queue=10",
        "min": "simple_p2p --delay 10ms --bandwidth 10 --queue 10"
    },
    {
        "name": "dl10_bw10_q24",
        "bytesreq": "5000000",
        "qns": "simple-p2p --delay=10ms --bandwidth=10Mbps --queue=24",
        "min": "simple_p2p --delay 10ms --bandwidth 10 --queue 24"
    },
    {
        "name": "dl5_bw20_q10",
        "bytesreq": "5000000",
        "qns": "simple-p2p --delay=5ms --bandwidth=20Mbps --queue=10",
        "min": "simple_p2p --delay 5ms --bandwidth 20 --queue 10"
    },
    {
        "name": "dl10_bw20_q20",
        "bytesreq": "5000000",
        "qns": "simple-p2p --delay=10ms --bandwidth=20Mbps --queue=20",
        "min": "simple_p2p --delay 10ms --bandwidth 20 --queue 20"
    },
    {
        "name": "dl25_bw20_q49",
        "bytesreq": "5000000",
        "qns": "simple-p2p --delay=25ms --bandwidth=20Mbps --queue=49",
        "min": "simple_p2p --delay 25ms --bandwidth 20 --queue 49"
    },
    {
        "name": "dl5_bw5_q2_reo500",
        "bytesreq": "5000000",
        "qns": "reorder --delay=5ms --bandwidth=5Mbps --queue=2 --reordergap=500",
        "min": "reorder --delay 5ms --bandwidth 5 --queue 2 --reordergap 500"
    },
    {
        "name": "dl10_bw5_q5_reo500",
        "bytesreq": "5000000",
        "qns": "reorder --delay=10ms --bandwidth=5Mbps --queue=5 --reordergap=500",
        "min": "reorder --delay 10ms --bandwidth 5 --queue 5 --reordergap 500"
    },
    {
        "name": "dl25_bw5_q12_reo500",
        "bytesreq": "5000000",
        "qns": "reorder --delay=25ms --bandwidth=5Mbps --queue=12 --reordergap=500",
        "min": "reorder --delay 25ms --bandwidth 5 --queue 12 --reordergap 500"
    },
    {
        "name": "dl5_bw10_q5_reo500",
        "bytesreq": "5000000",
        "qns": "reorder --delay=5ms --bandwidth=10Mbps --queue=5 --reordergap=500",
        "min": "reorder --delay 5ms --bandwidth 10 --queue 5 --reordergap 500"
    },
    {
        "name": "dl10_bw10_q10_reo500",
        "bytesreq": "5000000",
        "qns": "reorder --delay=10ms --bandwidth=10Mbps --queue=10 --reordergap=500",
        "min": "reorder --delay 10ms --bandwidth 10 --queue 10 --reordergap 500"
    },
    {
        "name": "dl25_bw10_q24_reo500",
        "bytesreq": "5000000",
        "qns": "reorder --delay=25ms --bandwidth=10Mbps --queue=24 --reordergap=500",
        "min": "reorder --delay 25ms --bandwidth 10 --queue 24 --reordergap 500"
    },
    {
        "name": "dl5_bw20_q10_reo500",
        "bytesreq": "5000000",
        "qns": "reorder --delay=5ms --bandwidth=20Mbps --queue=10 --reordergap=500",
        "min": "reorder --delay 5ms --bandwidth 20 --queue 10 --reordergap 500"
    },
    {
        "name": "dl10_bw20_q20_reo500",
        "bytesreq": "5000000",
        "qns": "reorder --delay=10ms --bandwidth=20Mbps --queue=20 --reordergap=500",
        "min": "reorder --delay 10ms --bandwidth 20 --queue 20 --reordergap 500"
    },
    {
        "name": "dl25_bw20_q49_reo500",
        "bytesreq": "5000000",
        "qns": "reorder --delay=25ms --bandwidth=20Mbps --queue=49 --reordergap=500",
        "min": "reorder --delay 25ms --bandwidth 20 --queue 49 --reordergap 500"
    },
]