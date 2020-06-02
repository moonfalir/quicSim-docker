#!/usr/bin/python
from argparse import ArgumentParser
import sys
import os
import time as ti

curdir = os.path.dirname(os.path.realpath(__file__))
sim_parser = ArgumentParser(description='Run mininet network simulator')
subparsers = sim_parser.add_subparsers(dest="scenario")

#Add simple p2p arguments
sub_parser = subparsers.add_parser('simple_p2p')
sub_parser.add_argument('-k', action='store_true', help='Flag to add kernel debug volume to container')
sys.path.append(curdir + '/simple_p2p')
from simple_p2p import Simple_p2p
p2p = Simple_p2p()
p2p.addCLIArguments(sub_parser)

#Add blackhole arguments
sub_parser = subparsers.add_parser('blackhole')
sub_parser.add_argument('-k', action='store_true', help='Flag to add kernel debug volume to container')
sys.path.append(curdir + '/blackhole')
from blackhole import Blackhole
blackhole = Blackhole()
blackhole.addCLIArguments(sub_parser)

#Add droplist arguments
sub_parser = subparsers.add_parser('droplist')
sub_parser.add_argument('-k', action='store_true', help='Flag to add kernel debug volume to container')
sys.path.append(curdir + '/droplist')
from droplist import Droplist
droplist = Droplist()
droplist.addCLIArguments(sub_parser)

#Add droprate arguments
sub_parser = subparsers.add_parser('droprate')
sub_parser.add_argument('-k', action='store_true', help='Flag to add kernel debug volume to container')
sys.path.append(curdir + '/droprate')
from droprate import Droprate
droprate = Droprate()
droprate.addCLIArguments(sub_parser)

sim_args = sim_parser.parse_args()

available_scenarios = ['simple_p2p']

def run_simple_p2p():
    entrypoint = "./entrypoint_min.sh"
    p2p = Simple_p2p()
    curtime = ti.strftime("%Y-%m-%d-%H-%M", ti.gmtime())
    p2p.run(sim_args, curtime, entrypoint)

def run_blackhole():
    entrypoint = "./entrypoint_min.sh"
    blackhole = Blackhole()
    curtime = ti.strftime("%Y-%m-%d-%H-%M", ti.gmtime())
    blackhole.run(sim_args, curtime, entrypoint)

def run_droplist():
    entrypoint = "./entrypoint_min.sh"
    droplist = Droplist()
    curtime = ti.strftime("%Y-%m-%d-%H-%M", ti.gmtime())
    droplist.run(sim_args, curtime, entrypoint)

def run_droprate():
    entrypoint = "./entrypoint_min.sh"
    droprate = Droprate()
    curtime = ti.strftime("%Y-%m-%d-%H-%M", ti.gmtime())
    droprate.run(sim_args, curtime, entrypoint)
    
switch = {
    'simple_p2p': run_simple_p2p,
    'blackhole': run_blackhole,
    'droplist': run_droplist,
    'droprate': run_droprate
}
func = switch.get(sim_args.scenario)
func()