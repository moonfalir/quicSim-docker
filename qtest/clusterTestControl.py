import copy, argparse, numpy, math, threading, json, paramiko
from qtest import QTestDist
from implementations import IMPLEMENTATIONS
from argparse import ArgumentParser

# install pip3
# install docker-compose
# install paramiko (via pip3) as sudo
# install docker (via pip3) as sudo
# install numpy (via pip3) as sudo


servers = [
    '172.19.13.223',
    '172.19.13.224',
    '172.19.13.225',
    '172.19.13.226',
    '172.19.13.227',
]
def serverThread(id, s_ip, testscenarios, username, password):
    serverssh = paramiko.SSHClient()
    serverssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    serverssh.connect(hostname=s_ip, username=username, password=password)

    shell = serverssh.invoke_shell()
    shell.send("cd ./quicSim-docker/qtest\n")
    shell.recv(9999)

    shell.send("echo \'" + json.dumps(testscenarios) + "\' > test.json\n")
    shell.recv(9999)

    shell.send("sudo python3 run.py --distid " + str(id) + "\n")
    shell.send(password + "\n")

    while True:
        if shell.recv_ready():
            resp = shell.recv(9999).decode("utf-8")
            if "Distributed testcases complete" in resp:
                break
            
    # run through testscenarios
        # create directory if needed
        # run docker command
        # process wireshark info and metrics
        # append server to list
    print("server " + s_ip + " testcases complete")

def main():
    qtest_parser = ArgumentParser(description='Run qtest simulations over cluster')
    qtest_parser.add_argument('--runs', action='store', type=int, nargs='?', const=1, default=1, help='Amount of runs of a single test')
    qtest_parser.add_argument('--usr', action='store', type=str, nargs='?',required=True, help='Username used for ssh connections')
    qtest_parser.add_argument('--pwd', action='store', type=str, nargs='?',required=True, help='Password used for ssh connections')
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
        x = threading.Thread(target=serverThread, args=(i, servers[i],splittestcases[i], qtest_args.usr, qtest_args.pwd))
        threads.append(x)
        x.start()

    # wait till server threads are finished
    for index, thread in enumerate(threads):
        thread.join()
    # gather all server log files on to this server
    # process metrics to get average values
    print("main")

main()