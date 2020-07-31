import json, os, re
import subprocess
from metriccalculator import MetricCalculator

class FileManager:
    
    def __init__(self):
        print("")
        self.serverqlog = ""

    def addTestInfo(self, testlogdir: str, scenario: str, clientpars: str, serverpars: str, clientname: str, servername: str, simulation: str):
        regex = re.compile("^(?![cs][lv]_).+\.qlog")
        files = []
        # find qlog files
        for dirpath, dirnames, filenames in os.walk(testlogdir):
            for f in filenames:
                if regex.match(f):
                    files.append(os.path.join(dirpath, f))

        for qlog in files:
            self.updateFile(
                qlog, 
                scenario, 
                simulation, 
                clientpars, 
                serverpars, 
                clientname, 
                servername,
                True if "client" in qlog or "clnt" in qlog else False
            )

    def updateFile(self, file: str, scenario: str, simulation: str, clparams: str, svparams: str, client: str, server: str, vantageclient: bool):
        newdata_file = {}
        commit = ""

        split_path = file.split(sep="/")
        sep ="/"

        # read used version (commit) of client/server
        if vantageclient:
            split_path[len(split_path) - 1] = "cl_commit.txt"
            commitpath = sep.join(split_path)
            with open(commitpath, "r") as commitfile:
                commit = commitfile.read()
            os.remove(commitpath)
        else:
            split_path[len(split_path) - 1] = "sv_commit.txt"
            commitpath = sep.join(split_path)
            with open(commitpath, "r") as commitfile:
                commit = commitfile.read()
            os.remove(commitpath)

        commit = commit.replace('\n', '')
        # create summary field for qlog
        newdata_file["summary"] = {
            "commit": commit,
            "simulation": simulation,
            "scenario": scenario,
            "client": client,
            "client_params": clparams,
            "server": server,
            "server_params": svparams
        }

        with open(file, "r") as qlog_file:
            data = qlog_file.read().lstrip()
            try:
                data_file = json.loads(data)
            except json.JSONDecodeError as err:
                print("Parsing qlog file error: " + err)
                return
            for key in data_file:
                if key != "summary":
                    newdata_file[key] = data_file[key]

        # remove and replace qlog file with new name
        os.remove(file)
        newfilename = ""
        if vantageclient:
            newfilename = "cl_"
        else:
            newfilename = "sv_"
        newfilename += simulation + "_"
        newfilename += client + "_" + server + ".qlog"

        split_path[len(split_path) - 1] = newfilename
        newpath = sep.join(split_path)

        if not vantageclient:
            self.serverqlog = newpath

        with open(newpath, "w") as qlog_file:
            json.dump(newdata_file, qlog_file)

    def pcaptojson(self, logdir: str, sim: str, met_calc: MetricCalculator, isquic: bool, run: int):
        # user wireshark docker image to convert pcap to json
        convertcmd = "docker run --env SIM=" + sim + " -v " + logdir + ":/logs:rw qtest-tshark"
        r = subprocess.run(convertcmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        regex = re.compile("^(?![cs][lv]_).+\.json")
        jsonfiles = []
        # find converted pcap files
        for dirpath, dirnames, filenames in os.walk(logdir):
            for f in filenames:
                if regex.match(f):
                    jsonfiles.append(os.path.join(dirpath, f))
        
        pcapfile = open(jsonfiles[0], 'r').read()
        decrypterrors = pcapfile.count("quic.decryption_failed")

        if decrypterrors < 1000:
            met_calc.calculateMetrics(logdir, jsonfiles, self.serverqlog, True, isquic, sim, run)
            
        # remove converted pcap files
        for jsonfile in jsonfiles:
            os.remove(jsonfile)     
        self.serverqlog = ""

        return (decrypterrors < 20)