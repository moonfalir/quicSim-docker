#!/usr/bin/env python3

import socket
import random
import string
from argparse import ArgumentParser

cl_parser = ArgumentParser(description='Run HTTP/0.9 server')
cl_parser.add_argument('--port', action='store', type=int, required=True, help='Port of http server')

sim_args = cl_parser.parse_args()

host = ""
port = sim_args.port

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen()

while True:
    conn, addr = s.accept()
    with conn:
        msg = conn.recv(10240).decode()
        
        split_msg = msg.split(sep="/")
        print(split_msg[len(split_msg) - 1])
        try:
            to_send = int(split_msg[len(split_msg) - 1])
        except:
            conn.close()
            exit()
        
        resp_msg = ''.join(random.choice(string.ascii_lowercase) for x in range(to_send))
        conn.send(resp_msg.encode())
        conn.close()