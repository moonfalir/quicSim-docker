#!/usr/bin/python
from sys import path
path.append('..')

from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink, Intf
from mininet.log import info, setLogLevel
from os import environ
from argparse import ArgumentParser, ArgumentTypeError
from time import sleep
from packetcapture import PacketCapture

class Blackhole:
    def check_positive(self, value):
        ivalue = int(value)
        if ivalue <= 0:
            raise ArgumentTypeError("%s is an invalid positive int value" % value)
        return ivalue
    def addCLIArguments(self, blackhole_parser):
        blackhole_parser.add_argument('--delay', action='store', type=str, required=True, help='One-way delay of network, specify with units.')
        blackhole_parser.add_argument('--bandwidth', action='store', type=float, required=True, help='Bandwidth of the link in Mbit/s.')
        blackhole_parser.add_argument('--queue', action='store', type=int, required=True, help='Queue size of the queue attached to the link. Specified in packets.')
        blackhole_parser.add_argument('--on', action='store', type=self.check_positive, required=True, help='Time period that traffic is allowed to flow.')
        blackhole_parser.add_argument('--off', action='store', type=self.check_positive, required=True, help='Time period that traffic is blocked.')
        blackhole_parser.add_argument('--repeat', action='store', type=self.check_positive, required=False, nargs='?', const=1, default=1, help='Repeat blocking and unblocking of traffic')
        blackhole_parser.add_argument('--direction', action='store', type=str, required=False, choices={'both', 'toclient', 'toserver'}, nargs='?', const='both', default='both', help='Specifiy the direction in which to block traffic.')

    def startTest(self, client, net, command, sim_args):
        # start quic client as background process
        client.cmd(command + " &")
        # fetch process id of quic client
        pid = client.cmd('echo $!')

        for i in range(0, sim_args.repeat):
            sleep(sim_args.on)
            info('Starting blackhole, traffic will be blocked\n')
            if (sim_args.direction == 'both' or sim_args.direction == 'toclient'):
                info('toclient off\n')
                # use tc to introduce 100% packet loss
                net.get('s2').cmd('tc qdisc change dev s2-eth1 parent 5:1 netem delay ' + sim_args.delay + ' loss 100% limit ' + str(sim_args.queue))
            if (sim_args.direction == 'both' or sim_args.direction == 'toserver'):
                info('toserver off\n')
                net.get('s1').cmd('tc qdisc change dev s1-eth1 parent 5:1 netem delay ' + sim_args.delay + ' loss 100% limit ' + str(sim_args.queue))
            
            sleep(sim_args.off)
            info('Stopping blackhole, traffic will be transmitted\n')
            if (sim_args.direction == 'both' or sim_args.direction == 'toclient'):
                info('toclient on\n')
                # use tc to remove 100% packet loss
                net.get('s2').cmd('tc qdisc change dev s2-eth1 parent 5:1 netem delay ' + sim_args.delay + ' limit ' + str(sim_args.queue))
            if (sim_args.direction == 'both' or sim_args.direction == 'toserver'):
                info('toserver on\n')
                net.get('s1').cmd('tc qdisc change dev s1-eth1 parent 5:1 netem delay ' + sim_args.delay + ' limit ' + str(sim_args.queue))

        # wait till quic client is finished before continueing
        client.cmd('wait ' + pid)

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

        net = Containernet(controller=Controller)
        info('*** Adding controller\n')
        net.addController('c0')
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
                               volumes=[cl_logdir + ':/logs'])

        info('*** Adding switches\n')
        s1 = net.addSwitch('s1')
        s2 = net.addSwitch('s2')
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
            self.startTest(server, net, entrypoint, sim_args)
        else:
            self.startTest(client, net, entrypoint, sim_args)
        # Wait some time to allow server finish writing to log file
        info('Test finished, waiting for server to receive all packets\n')
        sleep(3)
        capture.stopCapture()
        info('*** Stopping network\n')
        net.stop()
