#!/usr/bin/python
from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink, Intf
from mininet.log import info, setLogLevel
from os import environ
from argparse import ArgumentParser
from time import sleep

class Blackhole:
    def addCLIArguments(self, blackhole_parser):
        blackhole_parser.add_argument('--delay', action='store', type=str, required=True, help='One-way delay of network, specify with units.')
        blackhole_parser.add_argument('--bandwidth', action='store', type=float, required=True, help='Bandwidth of the link in Mbit/s.')
        blackhole_parser.add_argument('--queue', action='store', type=int, required=True, help='Queue size of the queue attached to the link. Specified in packets.')
        blackhole_parser.add_argument('--on', action='store', type=int, required=True, help='Time period that traffic is allowed to flow.')
        blackhole_parser.add_argument('--off', action='store', type=int, required=True, help='Time period that traffic is blocked.')
        blackhole_parser.add_argument('--repeat', action='store', type=int, required=False, help='Repeat blocking and unblocking of traffic')
        blackhole_parser.add_argument('--direction', action='store', type=int, required=False, help='Specifiy the direction in which to block traffic.')

    def startTest(self, client, net, command, sim_args):
        # start quic client as background process
        client.cmd(command + " &")
        # fetch process id of quic client
        pid = client.cmd('echo $!')

        sleep(sim_args.on)
        info('Starting blackhole, traffic will be blocked\n')
        net.get('server').cmd('tc qdisc change dev server-eth0 parent 5:1 netem delay ' + sim_args.delay + ' loss 100% limit ' + str(sim_args.queue))
        net.get('client').cmd('tc qdisc change dev client-eth0 parent 5:1 netem delay ' + sim_args.delay + ' loss 100% limit ' + str(sim_args.queue))
        
        sleep(sim_args.off)
        info('Stopping blackhole, traffic will be transmitted\n')
        net.get('server').cmd('tc qdisc change dev server-eth0 parent 5:1 netem delay ' + sim_args.delay + ' limit ' + str(sim_args.queue))
        net.get('client').cmd('tc qdisc change dev client-eth0 parent 5:1 netem delay ' + sim_args.delay + ' limit ' + str(sim_args.queue))

        # wait till quic client is finished before continueing
        client.cmd('wait ' + pid)

    def run(self, sim_args):
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
        p2p_link = net.addLink(server, client, cls=TCLink, delay=sim_args.delay, bw=sim_args.bandwidth, max_queue_size=sim_args.queue)
        info('*** Starting network\n')
        net.start()
        info('\n' + client_command + '\n')
        self.startTest(client, net, client_command, sim_args)
        # Wait some time to allow server finish writing to log file
        info('Test finished, waiting for server to receive all packets\n')
        sleep(3)
        info('*** Stopping network\n')
        net.stop()
