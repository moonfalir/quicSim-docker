import copy, argparse, numpy, math, threading, json, paramiko
from qtest import QTestDist
from implementations import IMPLEMENTATIONS
from argparse import ArgumentParser

# install pip3
# install docker-compose
# install paramiko (via pip3) as sudo
# install docker (via pip3) as sudo


servers = [
    '1',
    '2',
    '3',
    '4'
]
def serverThread(s_ip, testscenarios, username, password):
    serverssh = paramiko.SSHClient()
    serverssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #serverssh.connect(hostname=s_ip, username=username, password=password)
    # run through testscenarios
        # create directory if needed
        # run docker command
        # process wireshark info and metrics
        # append server to list
    #return testcase metrics
    if s_ip == "1":
        print("echo \'" + json.dumps(testscenarios) + "\' > test.json")

def main():
    qtest_parser = ArgumentParser(description='Run qtest simulations over cluster')
    qtest_parser.add_argument('--runs', action='store', type=int, nargs='?', const=1, default=1, help='Amount of runs of a single test')
    qtest_args = qtest_parser.parse_args()

    # gather all info for each test run
    implementations = copy.deepcopy(IMPLEMENTATIONS)
    testcases = QTestDist(
        implementations=implementations,
        runs=qtest_args.runs
    ).predetermineTestCases()

    # split info up in equal sizes for each server
    testsperserver = math.floor(len(testcases) / len(servers))
    remaintests = len(testcases) % len(servers)
    splittestcases = [testcases[x:x+testsperserver] for x in range(0, len(testcases), testsperserver)]

    if remaintests > 0:
        remaintests = 0 - remaintests
        remaincases = testcases[remaintests:]
        for i in range(len(remaincases)):
            splittestcases[i].append(remaincases[i])
    
    # run server threads
    threads = []
    for i in range(len(servers)):
        x = threading.Thread(target=serverThread, args=(servers[i],splittestcases[i], "test", "test2"))
        threads.append(x)
        x.start()

    # wait till server threads are finished
    for index, thread in enumerate(threads):
        thread.join()
    # gather all server log files on to this server
    # process metrics to get average values
    print("main")

main()