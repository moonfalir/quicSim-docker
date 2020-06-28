# inspiration: https://github.com/marten-seemann/quic-interop-runner
import logging, os, re, time, tempfile, subprocess, json
from filemanager import FileManager
from scenarios import SCENARIOS
from metriccalculator import MetricCalculator

class LogFileFormatter(logging.Formatter):
  def format(self, record):
    msg = super(LogFileFormatter, self).format(record)
    # remove color control characters
    return re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]').sub('', msg)

class QTest:
    _implementations = []
    _runs = 1
    def __init__(self, implementations: list, runs: int):
        self._implementations = implementations
        self._runs = runs
    
    def _run_testcase(self, serverid: int, clientid: int, rootlogdir: str, rootoutputdir: str, curtime: str, scenario: dict, met_calc: MetricCalculator, isquic: bool, run: int):
        if isquic:
            servers = self._implementations['quic_servers']
            clients = self._implementations['quic_clients']
        else:
            servers = self._implementations['tcp_servers']
            clients = self._implementations['tcp_clients']

        clientname = clients[clientid]['name']
        servername = servers[serverid]['name']
        
        testlogdir = rootlogdir + servername + "/" + scenario['name'] + "/run" + str(run + 1)
        testoutputdir = rootoutputdir + servername + "/" + scenario['name'] + "/run" + str(run + 1)

        if not os.path.isdir(testlogdir):
            os.makedirs(testlogdir)
            os.makedirs(testoutputdir)  

        bytesreq = scenario["bytesreq"]
        logging.debug("Request: %s bytes", bytesreq)
        tcpqns_config = ""
        if not isquic:
            tcpqns_config = "-f ../quic-network-simulator/docker-compose.tcp.yml "
        qnscmd = (
            "CURTIME=" + curtime + " "
            "SERVER_LOGS=" + testlogdir + " "
            "CLIENT_LOGS=" + testlogdir + " "
            "SCENARIO=\"" + scenario["qns"] + "\" "
            "CLIENT=" + clientname + " "
            "SERVER=" + servername + " "
            "BYTESREQ=" + bytesreq + " "
            "CLIENT_PARAMS=\"" + clients[clientid]['clpars_qns'] + "\" "
            "SERVER_PARAMS=\"" + servers[serverid]['svpars_qns'] + "\" "
            "CL_COMMIT=\"" + clients[clientid]['clcommit'] + "\" "
            "SV_COMMIT=\"" + servers[serverid]['svcommit'] + "\" "
            "docker-compose -f ../quic-network-simulator/docker-compose.yml " + tcpqns_config + "up --abort-on-container-exit"
        )

        print("Server: " + servername + ". Client: " + clientname + ". Test case: " + scenario["qns"] + ". Simulation: QNS")
        runsuccess = False
        filemngr = FileManager()
        while not runsuccess and "reorder" not in scenario["qns"]:
            try:
                r = subprocess.run(qnscmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=90)
                output = r.stdout
            except subprocess.TimeoutExpired as ex:
                output = ex.stdout
                expired = True

            with open(testoutputdir + "/qns.out", "w+") as outputfile:
                outputfile.write(output.decode('utf-8'))

            filemngr = FileManager()
            
            clpars = clients[clientid]['clpars_qns']
            clpars = clpars.replace("$CURTIME" , curtime)
            clpars = clpars.replace("$BYTESREQ", bytesreq)
            svpars = servers[serverid]['svpars_qns']
            svpars = svpars.replace("$CURTIME" , curtime)
            filemngr.addTestInfo(testlogdir, scenario["qns"], clpars, svpars, clientname, servername, "QNS")
            runsuccess = filemngr.pcaptojson(testlogdir, "QNS", met_calc, isquic, run)

        scenario_min = scenario["min"]
        if not isquic:
            scenario_min += " -k"
        mincmd = (
            "CURTIME=" + curtime + " "
            "SERVER_LOGS=" + testlogdir + " "
            "CLIENT_LOGS=" + testlogdir + " "
            "SCENARIO=\"" + scenario_min + "\" "
            "CLIENT=" + clientname + " "
            "SERVER=" + servername + " "
            "BYTESREQ=" + bytesreq + " "
            "CLIENT_PARAMS=\"" + clients[clientid]['clpars_min'] + "\" "
            "SERVER_PARAMS=\"" + servers[serverid]['svpars_min'] + "\" "
            "CL_COMMIT=\"" + clients[clientid]['clcommit'] + "\" "
            "SV_COMMIT=\"" + servers[serverid]['svcommit'] + "\" "
            "docker-compose -f ../containernet/docker-compose.yml up --abort-on-container-exit"
        )
        print("Server: " + servername + ". Client: " + clientname + ". Test case: " + scenario["min"] + ". Simulation: MININET")
        runsuccess = False
        while not runsuccess:
            try:
                r = subprocess.run(mincmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=90)
                output = r.stdout
            except subprocess.TimeoutExpired as ex:
                output = ex.stdout
                expired = True

            with open(testoutputdir + "/min.out", "w+") as outputfile:
                outputfile.write(output.decode('utf-8'))
            
            clpars = clients[clientid]['clpars_min']
            clpars = clpars.replace("$CURTIME" , curtime)
            clpars = clpars.replace("$BYTESREQ", bytesreq)
            svpars = servers[serverid]['svpars_min']
            svpars = svpars.replace("$CURTIME" , curtime)
            filemngr.addTestInfo(testlogdir, scenario["min"], clpars, svpars, clientname, servername, "MIN")
            runsuccess = filemngr.pcaptojson(testlogdir, "MIN", met_calc, isquic, run)

    def run(self):
        curtime = time.strftime("%Y-%m-%d-%H-%M", time.gmtime())
        rootlogdir = os.path.dirname(os.path.abspath(__file__)) + "/logs/" + curtime
        rootoutputdir = os.path.dirname(os.path.abspath(__file__)) + "/outputs/" + curtime
        os.makedirs(rootlogdir)
        os.makedirs(rootoutputdir)
        rootlogdir += "/"
        rootoutputdir += "/"

        met_calc = MetricCalculator()

        with open(rootlogdir + "scenarios.json", "w+") as sc_file:
            json.dump(SCENARIOS, sc_file, indent=4, separators=(',', ': '))
        with open(rootoutputdir + "scenarios.json", "w+") as sc_file:
            json.dump(SCENARIOS, sc_file, indent=4, separators=(',', ': '))
        for serverid, server in enumerate(self._implementations['quic_servers']):
            for clientid, client in enumerate(self._implementations['quic_clients']):
                for scenario in SCENARIOS:
                    for run in range(0, self._runs):
                        self._run_testcase(serverid, clientid, rootlogdir, rootoutputdir, curtime, scenario, met_calc, True, run)

        for serverid, server in enumerate(self._implementations['tcp_servers']):
            for clientid, client in enumerate(self._implementations['tcp_clients']):
                for scenario in SCENARIOS:
                    for run in range(0, self._runs):
                        self._run_testcase(serverid, clientid, rootlogdir, rootoutputdir, curtime, scenario, met_calc, False, run)

        met_calc.saveMetrics(rootlogdir)


class QTestDist:
    _implementations = []
    _runs = 1
    def __init__(self, implementations: list, runs: int):
        self._implementations = implementations
        self._runs = runs

    def getTestCaseInfo(self, serverid: int, clientid: int, rootlogdir: str, rootoutputdir: str, curtime: str, scenario: dict, isquic: bool, run: int, testlist: list):
        if isquic:
            servers = self._implementations['quic_servers']
            clients = self._implementations['quic_clients']
        else:
            servers = self._implementations['tcp_servers']
            clients = self._implementations['tcp_clients']

        clientname = clients[clientid]['name']
        servername = servers[serverid]['name']
    
        testlogdir = rootlogdir + servername + "/" + scenario['name'] + "/run" + str(run + 1)
        testoutputdir = rootoutputdir + servername + "/" + scenario['name'] + "/run" + str(run + 1)   

        bytesreq = scenario["bytesreq"]
        logging.debug("Request: %s bytes", bytesreq)
        tcpqns_config = ""
        if not isquic:
            tcpqns_config = "-f ../quic-network-simulator/docker-compose.tcp.yml "
        
        testcase = {
            "testlogdir": testlogdir,
            "testoutputdir": testoutputdir,
            "curtime": curtime,
            "bytesreq": bytesreq,
            "tcp_config": tcpqns_config,
            "sim": "qns",
            "scenario": scenario["qns"],
            "client": clientname,
            "server": servername,
            "run": run,
            "client_params": clients[clientid]['clpars_qns'],
            "server_params": servers[serverid]['svpars_qns'],
            "cl_commit": clients[clientid]['clcommit'],
            "sv_commit": servers[serverid]['svcommit']
        }
        if "reorder" not in scenario["qns"]:
            testlist.append(testcase)

        scenario_min = scenario["min"]
        tcp_config = ""
        if not isquic:
            scenario_min += " -k"
            tcp_config = "tcpmin"

        testcase = {
            "testlogdir": testlogdir,
            "testoutputdir": testoutputdir,
            "curtime": curtime,
            "bytesreq": bytesreq,
            "tcp_config": tcp_config,
            "sim": "min",
            "scenario": scenario_min,
            "client": clientname,
            "server": servername,
            "run": run,
            "client_params": clients[clientid]['clpars_min'],
            "server_params": servers[serverid]['svpars_min'],
            "cl_commit": clients[clientid]['clcommit'],
            "sv_commit": servers[serverid]['svcommit']
        }
        testlist.append(testcase)
        
        return testlist

    def predetermineTestCases(self):
        curtime = time.strftime("%Y-%m-%d-%H-%M", time.gmtime())
        rootlogdir = "/home/jreynders/quicSim-docker/qtest/logs/" + curtime
        rootoutputdir = "/home/jreynders/quicSim-docker/qtest/outputs/" + curtime
        
        rootlogdir += "/"
        rootoutputdir += "/"

        testcases = []

        for serverid, server in enumerate(self._implementations['quic_servers']):
            for clientid, client in enumerate(self._implementations['quic_clients']):
                for scenario in SCENARIOS:
                    for run in range(0, self._runs):
                        testcases = self.getTestCaseInfo(serverid, clientid, rootlogdir, rootoutputdir, curtime, scenario, True, run, testcases)

        for serverid, server in enumerate(self._implementations['tcp_servers']):
            for clientid, client in enumerate(self._implementations['tcp_clients']):
                for scenario in SCENARIOS:
                    for run in range(0, self._runs):
                        testcases = self.getTestCaseInfo(serverid, clientid, rootlogdir, rootoutputdir, curtime, scenario, False, run, testcases)

        return testcases, curtime
    
    def runDistTestCase(self, testcase, met_calc):
        #create logdir
        if not os.path.isdir(testcase["testlogdir"]):
            os.makedirs(testcase["testlogdir"])
            os.makedirs(testcase["testoutputdir"])
        bytesreq = testcase["bytesreq"]
        isquic = testcase["tcp_config"] == ""
        cmd = (
            "CURTIME=" + testcase["curtime"] + " "
            "SERVER_LOGS=" + testcase["testlogdir"] + " "
            "CLIENT_LOGS=" + testcase["testlogdir"] + " "
            "SCENARIO=\"" + testcase["scenario"] + "\" "
            "CLIENT=" + testcase["client"] + " "
            "SERVER=" + testcase["server"] + " "
            "BYTESREQ=" + bytesreq + " "
            "CLIENT_PARAMS=\"" + testcase["client_params"] + "\" "
            "SERVER_PARAMS=\"" + testcase["server_params"] + "\" "
            "CL_COMMIT=\"" + testcase['cl_commit'] + "\" "
            "SV_COMMIT=\"" + testcase['sv_commit'] + "\" "
        )
        if testcase["sim"] == "qns":
            o_file = "/qns.out"
            cmd = cmd + "docker-compose -f ../quic-network-simulator/docker-compose.yml " + testcase["tcp_config"] + "up --abort-on-container-exit"
        else:
            o_file = "/min.out"
            cmd = cmd + "docker-compose -f ../containernet/docker-compose.yml up --abort-on-container-exit"
        print("Server: " + testcase["server"] + ". Client: " + testcase["client"] + ". Test case: " + testcase["scenario"] + ". Simulation: " + testcase["sim"])
        runsuccess = False
        while not runsuccess:
            try:
                r = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=90)
                output = r.stdout
            except subprocess.TimeoutExpired as ex:
                output = ex.stdout
                expired = True


            with open(testcase["testoutputdir"] + o_file, "w+") as outputfile:
                outputfile.write(output.decode('utf-8'))

            filemngr = FileManager()
            
            clpars = testcase["client_params"]
            clpars = clpars.replace("$CURTIME" , testcase["curtime"])
            clpars = clpars.replace("$BYTESREQ", bytesreq)
            svpars = testcase["server_params"]
            svpars = svpars.replace("$CURTIME" , testcase["curtime"])
            filemngr.addTestInfo(testcase["testlogdir"], testcase["scenario"], clpars, svpars, testcase["client"], testcase["client"], testcase["sim"])
            runsuccess = filemngr.pcaptojson(testcase["testlogdir"], testcase["sim"], met_calc, isquic, testcase["run"])

    def runDistributed(self, id):
        testcasesfile = open(os.path.dirname(os.path.abspath(__file__)) + "/test.json", "r")
        testcases = json.load(testcasesfile)
        met_calc = MetricCalculator()

        for testcase in testcases:
           self.runDistTestCase(testcase, met_calc)
        
        metrics = met_calc.getMetrics()
        split_dir = testcases[0]["testlogdir"].split("/")
        split_dir = split_dir[0:len(split_dir) - 3]
        outputdir = "/".join(split_dir)
        
        with open(outputdir + "/metrics" + str(id) + ".json", mode='w') as metrics_file:
            json.dump(metrics, metrics_file)