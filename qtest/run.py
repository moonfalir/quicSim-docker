# inspiration: https://github.com/marten-seemann/quic-interop-runner

import copy, argparse
from qtest import QTest
from implementations import IMPLEMENTATIONS
from argparse import ArgumentParser

qtest_parser = ArgumentParser(description='Run qtest simulations')
qtest_parser.add_argument('--runs', action='store', type=int, nargs='?', const=1, default=1, help='Amount of runs of a single test')
qtest_args = qtest_parser.parse_args()

implementations = copy.deepcopy(IMPLEMENTATIONS)


QTest(
    implementations=implementations,
    runs=qtest_args.runs
).run()