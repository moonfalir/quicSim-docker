# inspiration: https://github.com/marten-seemann/quic-interop-runner
import logging, os, re, time, tempfile, subprocess
from qlogmanager import QlogManager

class LogFileFormatter(logging.Formatter):
  def format(self, record):
    msg = super(LogFileFormatter, self).format(record)
    # remove color control characters
    return re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]').sub('', msg)

class QTest:
    _implementations = []
    def __init__(self, implementations: list):
        self._implementations = implementations
    
    def _run_testcase(self, serverid: int, clientid: int, rootlogdir: str, rootoutputdir: str, curtime: str):
        clientname = self._implementations[clientid]['name']
        servername = self._implementations[serverid]['name']
        if not os.path.isdir(rootlogdir + servername):
            os.makedirs(rootlogdir + servername)
            os.makedirs(rootoutputdir + servername)
        testlogdir = rootlogdir + servername + "/" + clientname
        testoutputdir = rootoutputdir + servername + "/" + clientname
        os.makedirs(testlogdir)
        os.makedirs(testoutputdir)

        bytesreq = 5000000
        logging.debug("Request: %d bytes", bytesreq)
        scenario = "simple-p2p --delay=15ms --bandwidth=5Mbps --queue=25"
        qnscmd = (
            "CURTIME=" + curtime + " "
            "SERVER_LOGS=" + testlogdir + " "
            "CLIENT_LOGS=" + testlogdir + " "
            "SCENARIO=\"" + scenario + "\" "
            "CLIENT=" + clientname + " "
            "SERVER=" + servername + " "
            "BYTESREQ=" + str(bytesreq) + " "
            "CLIENT_PARAMS=\"" + self._implementations[clientid]['clpars_qns'] + "\" "
            "SERVER_PARAMS=\"" + self._implementations[serverid]['svpars_qns'] + "\" "
            "CL_COMMIT=\"" + self._implementations[clientid]['clcommit'] + "\" "
            "SV_COMMIT=\"" + self._implementations[serverid]['svcommit'] + "\" "
            "docker-compose -f ../quic-network-simulator/docker-compose.yml up --abort-on-container-exit"
        )

        print("Server: " + servername + ". Client: " + clientname + ". Test case: " + scenario + ". Simulation: QNS")
        try:
            r = subprocess.run(qnscmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
            output = r.stdout
        except subprocess.TimeoutExpired as ex:
            output = ex.stdout
            expired = True

        with open(testoutputdir + "/qns.out", "w+") as outputfile:
            outputfile.write(output.decode('utf-8'))

        qlogmngr = QlogManager()
        clpars = self._implementations[clientid]['clpars_qns']
        clpars = clpars.replace("$CURTIME" , curtime)
        clpars = clpars.replace("$BYTESREQ", str(bytesreq))
        svpars = self._implementations[serverid]['svpars_qns']
        svpars = svpars.replace("$CURTIME" , curtime)
        qlogmngr.addTestInfo(testlogdir, scenario, clpars, svpars, clientname, servername, "QNS")

        scenario = "simple_p2p --delay 15ms --bandwidth 5 --queue 25"
        qnscmd = (
            "CURTIME=" + curtime + " "
            "SERVER_LOGS=" + testlogdir + " "
            "CLIENT_LOGS=" + testlogdir + " "
            "SCENARIO=\"" + scenario + "\" "
            "CLIENT=" + clientname + " "
            "SERVER=" + servername + " "
            "BYTESREQ=" + str(bytesreq) + " "
            "CLIENT_PARAMS=\"" + self._implementations[clientid]['clpars_min'] + "\" "
            "SERVER_PARAMS=\"" + self._implementations[serverid]['svpars_min'] + "\" "
            "CL_COMMIT=\"" + self._implementations[clientid]['clcommit'] + "\" "
            "SV_COMMIT=\"" + self._implementations[serverid]['svcommit'] + "\" "
            "docker-compose -f ../containernet/docker-compose.yml up --abort-on-container-exit"
        )
        print("Server: " + servername + ". Client: " + clientname + ". Test case: " + scenario + ". Simulation: MININET")
        try:
            r = subprocess.run(qnscmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=90)
            output = r.stdout
        except subprocess.TimeoutExpired as ex:
            output = ex.stdout
            expired = True

        with open(testoutputdir + "/min.out", "w+") as outputfile:
            outputfile.write(output.decode('utf-8'))
        
        clpars = self._implementations[clientid]['clpars_min']
        clpars = clpars.replace("$CURTIME" , curtime)
        clpars = clpars.replace("$BYTESREQ", str(bytesreq))
        svpars = self._implementations[serverid]['svpars_min']
        svpars = svpars.replace("$CURTIME" , curtime)
        qlogmngr.addTestInfo(testlogdir, scenario, clpars, svpars, clientname, servername, "MIN")

    def run(self):
        curtime = time.strftime("%Y-%m-%d-%H-%M", time.gmtime())
        rootlogdir = os.path.dirname(os.path.abspath(__file__)) + "/logs/" + curtime
        rootoutputdir = os.path.dirname(os.path.abspath(__file__)) + "/outputs/" + curtime
        os.makedirs(rootlogdir)
        os.makedirs(rootoutputdir)
        rootlogdir += "/"
        rootoutputdir += "/"

        # TODO: run testcases for all servers and clients
        # self._run_testcase(3, 3, rootlogdir, curtime)

        #for serverid, server in enumerate(self._implementations):
        #    for clientid, client in enumerate(self._implementations):
        self._run_testcase(1, 0, rootlogdir, rootoutputdir, curtime)