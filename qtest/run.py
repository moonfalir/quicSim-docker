# inspiration: https://github.com/marten-seemann/quic-interop-runner

import copy, argparse
from qtest import QTest, QTestDist
from implementations import IMPLEMENTATIONS
from argparse import ArgumentParser

qtest_parser = ArgumentParser(description='Run qtest simulations')
qtest_parser.add_argument('--runs', action='store', type=int, nargs='?', const=1, default=1, help='Amount of runs of a single test')
qtest_parser.add_argument('--distid', action='store', type=int, nargs='?', const=-1, default=-1, help="Run in distributed mode for server cluster")
qtest_args = qtest_parser.parse_args()

implementations = copy.deepcopy(IMPLEMENTATIONS)

if qtest_args.distid > -1:
    QTestDist(
        implementations=[],
        runs=0
    ).runDistributed(qtest_args.distid)
else:
    QTest(
        implementations=implementations,
        runs=qtest_args.runs
    ).run()