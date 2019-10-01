#!/usr/bin/python
from argparse import ArgumentParser
import sys
import os

curdir = os.path.dirname(os.path.realpath(__file__))
sim_parser = ArgumentParser(description='Run mininet network simulator')
subparsers = sim_parser.add_subparsers(dest="scenario")

#Add simple p2p arguments
sub_parser = subparsers.add_parser('simple_p2p')
sys.path.append(curdir + '/simple_p2p')
from simple_p2p import Simple_p2p
p2p = Simple_p2p()
p2p.addCLIArguments(sub_parser)

#Add blackhole arguments
sub_parser = subparsers.add_parser('blackhole')
sys.path.append(curdir + '/blackhole')
from blackhole import Blackhole
blackhole = Blackhole()
blackhole.addCLIArguments(sub_parser)

sim_args = sim_parser.parse_args()

available_scenarios = ['simple_p2p']

def run_simple_p2p():
    p2p = Simple_p2p()
    p2p.run(sim_args)

def run_blackhole():
    blackhole = Blackhole()
    blackhole.run(sim_args)

switch = {
    'simple_p2p': run_simple_p2p,
    'blackhole': run_blackhole
}
func = switch.get(sim_args.scenario)
func()