#!/usr/bin/env python3

import socket
from argparse import ArgumentParser

cl_parser = ArgumentParser(description='Run HTTP/0.9 client')
cl_parser.add_argument('--ip', action='store', type=str, required=True, help='Ip address of http server')
cl_parser.add_argument('--port', action='store', type=int, required=True, help='Port of http server')
cl_parser.add_argument('--bytes', action='store', type=int, required=True, help='Amount of bytes to request from server')

sim_args = cl_parser.parse_args()

host = sim_args.ip  # The server's hostname or IP address
port = sim_args.port        # The port used by the server

bytes_requested = sim_args.bytes

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))
    s.sendall(('GET http://www.example.com/' + str(sim_args.bytes)).encode())

    resp = ''

    while len(resp) < bytes_requested:
        resp += s.recv(10240).decode()

    print("Bytes received: " + str(bytes_requested))