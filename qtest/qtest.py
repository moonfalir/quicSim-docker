# inspiration: https://github.com/marten-seemann/quic-interop-runner
import logging, os, re, time, tempfile, subprocess, json
from qlogmanager import QlogManager
from scenarios import SCENARIOS

class LogFileFormatter(logging.Formatter):
  def format(self, record):
    msg = super(LogFileFormatter, self).format(record)
    # remove color control characters
    return re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]').sub('', msg)

class QTest:
    _implementations = []
    def __init__(self, implementations: list):
        self._implementations = implementations
    
    def _run_testcase(self, serverid: int, clientid: int, rootlogdir: str, rootoutputdir: str, curtime: str, scenario: dict):
        servers = self._implementations['servers']
        clients = self._implementations['clients']
        clientname = clients[clientid]['name']
        servername = servers[serverid]['name']
        if not os.path.isdir(rootlogdir + servername):
            os.makedirs(rootlogdir + servername)
            os.makedirs(rootoutputdir + servername)
        testlogdir = rootlogdir + servername + "/" + clientname
        testoutputdir = rootoutputdir + servername + "/" + clientname

        if not os.path.isdir(testlogdir):
            os.makedirs(testlogdir)
            os.makedirs(testoutputdir)

        testlogdir += "/" + scenario['name'] 
        testoutputdir += "/" + scenario['name']    

        os.makedirs(testlogdir)
        os.makedirs(testoutputdir)  

        bytesreq = 5000000
        logging.debug("Request: %d bytes", bytesreq)
        qnscmd = (
            "CURTIME=" + curtime + " "
            "SERVER_LOGS=" + testlogdir + " "
            "CLIENT_LOGS=" + testlogdir + " "
            "SCENARIO=\"" + scenario["qns"] + "\" "
            "CLIENT=" + clientname + " "
            "SERVER=" + servername + " "
            "BYTESREQ=" + str(bytesreq) + " "
            "CLIENT_PARAMS=\"" + clients[clientid]['clpars_qns'] + "\" "
            "SERVER_PARAMS=\"" + servers[serverid]['svpars_qns'] + "\" "
            "CL_COMMIT=\"" + clients[clientid]['clcommit'] + "\" "
            "SV_COMMIT=\"" + servers[serverid]['svcommit'] + "\" "
            "docker-compose -f ../quic-network-simulator/docker-compose.yml up --abort-on-container-exit"
        )

        print("Server: " + servername + ". Client: " + clientname + ". Test case: " + scenario["qns"] + ". Simulation: QNS")
        try:
            r = subprocess.run(qnscmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=90)
            output = r.stdout
        except subprocess.TimeoutExpired as ex:
            output = ex.stdout
            expired = True

        with open(testoutputdir + "/qns.out", "w+") as outputfile:
            outputfile.write(output.decode('utf-8'))

        qlogmngr = QlogManager()
        clpars = clients[clientid]['clpars_qns']
        clpars = clpars.replace("$CURTIME" , curtime)
        clpars = clpars.replace("$BYTESREQ", str(bytesreq))
        svpars = servers[serverid]['svpars_qns']
        svpars = svpars.replace("$CURTIME" , curtime)
        qlogmngr.addTestInfo(testlogdir, scenario["qns"], clpars, svpars, clientname, servername, "QNS")

        mincmd = (
            "CURTIME=" + curtime + " "
            "SERVER_LOGS=" + testlogdir + " "
            "CLIENT_LOGS=" + testlogdir + " "
            "SCENARIO=\"" + scenario["min"] + "\" "
            "CLIENT=" + clientname + " "
            "SERVER=" + servername + " "
            "BYTESREQ=" + str(bytesreq) + " "
            "CLIENT_PARAMS=\"" + clients[clientid]['clpars_min'] + "\" "
            "SERVER_PARAMS=\"" + servers[serverid]['svpars_min'] + "\" "
            "CL_COMMIT=\"" + clients[clientid]['clcommit'] + "\" "
            "SV_COMMIT=\"" + servers[serverid]['svcommit'] + "\" "
            "docker-compose -f ../containernet/docker-compose.yml up --abort-on-container-exit"
        )
        print("Server: " + servername + ". Client: " + clientname + ". Test case: " + scenario["min"] + ". Simulation: MININET")
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
        clpars = clpars.replace("$BYTESREQ", str(bytesreq))
        svpars = servers[serverid]['svpars_min']
        svpars = svpars.replace("$CURTIME" , curtime)
        qlogmngr.addTestInfo(testlogdir, scenario["min"], clpars, svpars, clientname, servername, "MIN")

    def run(self):
        curtime = time.strftime("%Y-%m-%d-%H-%M", time.gmtime())
        rootlogdir = os.path.dirname(os.path.abspath(__file__)) + "/logs/" + curtime
        rootoutputdir = os.path.dirname(os.path.abspath(__file__)) + "/outputs/" + curtime
        os.makedirs(rootlogdir)
        os.makedirs(rootoutputdir)
        rootlogdir += "/"
        rootoutputdir += "/"

        with open(rootlogdir + "scenarios.json", "w+") as sc_file:
            json.dump(SCENARIOS, sc_file, indent=4, separators=(',', ': '))
        with open(rootoutputdir + "scenarios.json", "w+") as sc_file:
            json.dump(SCENARIOS, sc_file, indent=4, separators=(',', ': '))
        for serverid, server in enumerate(self._implementations['servers']):
            for clientid, client in enumerate(self._implementations['clients']):
                for scenario in SCENARIOS:
                    self._run_testcase(serverid, clientid, rootlogdir, rootoutputdir, curtime, scenario)