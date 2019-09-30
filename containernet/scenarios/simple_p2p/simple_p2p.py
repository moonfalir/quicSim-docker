#!/usr/bin/python
from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink, Intf
from mininet.log import info, setLogLevel
from os import environ
from argparse import ArgumentParser
from time import sleep

class Simple_p2p:
    def run(self, sim_args):
        #sim_parser = ArgumentParser(description='Run mininet network simulator')
        #sim_parser.add_argument('--delay', action='store', type=str, required=True, help='One-way delay of network, specify with units.')
        #sim_parser.add_argument('--bandwidth', action='store', type=float, required=True, help='Bandwidth of the link in Mbit/s.')
        #sim_parser.add_argument('--queue', action='store', type=int, required=True, help='Queue size of the queue attached to the link. Specified in packets.')
        #sim_args = sim_parser.parse_args()

        if any(v not in environ for v in ['CLIENT', 'CLIENT_PARAMS', 'SERVER', 'SERVER', 'LOGDIR']):
            # TODO show help
            exit(1)
        client_image = environ['CLIENT']
        client_command = environ['CLIENT_PARAMS']
        server_image = environ['SERVER']
        server_command = environ['SERVER_PARAMS']
        logdir = environ['LOGDIR']

        setLogLevel('info')

        net = Containernet(controller=Controller)
        info('*** Adding controller\n')
        net.addController('c0')
        info('*** Adding docker containers\n')
        server = net.addDocker('server', ip='10.0.0.251',
                               dimage=server_image + ":latest",
                               dcmd=server_command,
                               volumes=[logdir + '/logs/server:/logs'])
        client = net.addDocker('client', ip='10.0.0.252', 
                               dimage=client_image + ":latest", 
                               volumes=[logdir + '/logs/client:/logs'])

        info('*** Creating links\n')
        net.addLink(server, client, cls=TCLink, delay=sim_args.delay, bw=sim_args.bandwidth, max_queue_size=sim_args.queue)
        info('*** Starting network\n')
        net.start()
        info('\n' + client_command + '\n')
        info(client.cmd(client_command) + "\n")
        # Wait some time to allow server finish writing to log file
        sleep(5)
        info('*** Stopping network')
        net.stop()
