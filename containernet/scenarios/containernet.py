#!/usr/bin/python
from argparse import ArgumentParser
import sys
import os

sim_parser = ArgumentParser(description='Run mininet network simulator')
subparsers = sim_parser.add_subparsers(dest="scenario")
p2p_parser = subparsers.add_parser('simple_p2p')
p2p_parser.add_argument('--delay', action='store', type=str, required=True, help='One-way delay of network, specify with units.')
p2p_parser.add_argument('--bandwidth', action='store', type=float, required=True, help='Bandwidth of the link in Mbit/s.')
p2p_parser.add_argument('--queue', action='store', type=int, required=True, help='Queue size of the queue attached to the link. Specified in packets.')

sim_args = sim_parser.parse_args()

available_scenarios = ['simple_p2p']

curdir = os.path.dirname(os.path.realpath(__file__))
def run_simple_p2p():
    sys.path.append(curdir + '/simple_p2p')
    from simple_p2p import Simple_p2p
    scenario = Simple_p2p()
    scenario.run(sim_args)

switch = {
    'simple_p2p': run_simple_p2p
}
func = switch.get(sim_args.scenario)
func()