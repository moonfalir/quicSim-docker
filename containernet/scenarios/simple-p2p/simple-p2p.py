#!/usr/bin/python
from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink, Intf
from mininet.log import info, setLogLevel
from os import environ

if any(v not in environ for v in ['CLIENT', 'CLIENT_PARAMS', 'SERVER', 'SERVER']):
    # TODO show help
    exit(1)
client_image = environ['CLIENT']
client_command = environ['CLIENT_PARAMS']
server_image = environ['SERVER']
server_command = environ['SERVER_PARAMS']

setLogLevel('info')

net = Containernet(controller=Controller)
info('*** Adding controller\n')
net.addController('c0')
info('*** Adding docker containers\n')
server = net.addDocker('server', ip='10.0.0.251',
                       dimage=server_image + ":latest",
                       dcmd=server_command)
client = net.addDocker('client', ip='10.0.0.252', dimage=client_image + ":latest")
info('*** Creating links\n')
net.addLink(server, client, cls=TCLink, delay='100ms', bw=1)
info('*** Starting network\n')
net.start()
info('\n' + client_command + '\n')
info(client.cmd(client_command) + "\n")
info('*** Stopping network')
net.stop()
