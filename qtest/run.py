# inspiration: https://github.com/marten-seemann/quic-interop-runner

import copy
from qtest import QTest
from implementations import IMPLEMENTATIONS


implementations = copy.deepcopy(IMPLEMENTATIONS)

QTest(
    implementations=implementations
).run()