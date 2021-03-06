#!/usr/bin/python
from sys import path
path.append('..')

from mininet.net import Containernet
from mininet.node import POX, OVSController
from mininet.cli import CLI
from mininet.link import TCLink, Intf
from mininet.log import info, setLogLevel
from os import environ
from argparse import ArgumentParser
from time import sleep
from packetcapture import PacketCapture

class Droplist:
    def addCLIArguments(self, p2p_parser):
        p2p_parser.add_argument('--delay', action='store', type=str, required=True, help='One-way delay of network, specify with units.')
        p2p_parser.add_argument('--bandwidth', action='store', type=float, required=True, help='Bandwidth of the link in Mbit/s.')
        p2p_parser.add_argument('--queue', action='store', type=int, required=True, help='Queue size of the queue attached to the link. Specified in packets.')
        p2p_parser.add_argument('--drops_to_client', action='store', type=str, required=False, help="Index of packets send to the client that need to be dropped")
        p2p_parser.add_argument('--drops_to_server', action='store', type=str, required=False, help="Index of packets send to the server that need to be dropped")

    def run(self, sim_args, curtime, entrypoint):
        if any(v not in environ for v in ['CLIENT', 'CLIENT_PARAMS', 'SERVER', 'SERVER', 'CLIENT_LOGS', 'SERVER_LOGS', 'CL_COMMIT', 'SV_COMMIT']):
            # TODO show help
            exit(1)
        client_image = environ['CLIENT']
        client_params = environ['CLIENT_PARAMS']
        server_image = environ['SERVER']
        server_params = environ['SERVER_PARAMS']
        cl_logdir = environ['CLIENT_LOGS']
        sv_logdir = environ['SERVER_LOGS']
        clcommit = environ['CL_COMMIT']
        svcommit = environ['SV_COMMIT']

        setLogLevel('info')

        net = Containernet(controller=POX)
        info('*** Adding controller\n')
        poxCommand = 'forwarding.droplist'
        
        if sim_args.drops_to_client != None:
            poxCommand += ' --droplist_server=' + sim_args.drops_to_client

        if sim_args.drops_to_server != None:
            poxCommand += ' --droplist_client=' + sim_args.drops_to_server
        
        # add custom controller to drop list of packets
        net.addController('c0', poxArgs = poxCommand)
        info('*** Adding docker containers\n')
        server_vs = [sv_logdir + ':/logs']
        # add kernel debug volume to allow eBPF code to run
        if sim_args.k:
            server_vs.append( '/sys/kernel/debug:/sys/kernel/debug:ro')
        server = net.addDocker('server', ip='10.0.0.251',
                               environment={"ROLE": "server", "SERVER_PARAMS": server_params, "COMMIT": svcommit},
                               dimage=server_image + ":latest",
                               volumes=server_vs)
        client = net.addDocker('client', ip='10.0.0.252',
                               environment={"ROLE": "client", "CLIENT_PARAMS": client_params, "COMMIT": clcommit}, 
                               dimage=client_image + ":latest", 
                               volumes=[cl_logdir + '/logs'])
        info('*** Adding switch\n')
        s1 = net.addSwitch('s1')
        s2 = net.addSwitch('s2', controller=OVSController)
        info('*** Creating links\n')
        net.addLink(s1, s2, cls=TCLink, delay=sim_args.delay, bw=sim_args.bandwidth, max_queue_size=sim_args.queue)
        net.addLink(s1, client)
        net.addLink(s2, server)
        info('\n*** Updating and building client/server\n')
        server.cmd('./updateAndBuild.sh')
        client.cmd('./updateAndBuild.sh')
        info('*** Starting network\n')
        net.start()
        capture = PacketCapture()
        if sim_args.k:
            client.cmd(entrypoint + " &")
        else:
            server.cmd(entrypoint + " &" )
        capture.startCapture()
        info('\n' + entrypoint + '\n')
        if sim_args.k:
            info(server.cmd(entrypoint) + "\n")
        else:
            info(client.cmd(entrypoint) + "\n")
        # Wait some time to allow server finish writing to log file
        sleep(3)
        capture.stopCapture()
        info('*** Stopping network')
        net.stop()
