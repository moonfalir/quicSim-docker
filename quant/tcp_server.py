#!/usr/bin/env python3

import socket
import random
import string
from argparse import ArgumentParser

cl_parser = ArgumentParser(description='Run TCP socket server')
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
        conn.close()
        exit(0)