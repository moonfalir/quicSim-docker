import json, os, re
import subprocess
from metriccalculator import MetricCalculator

class FileManager:
    _tshark_path = "/home/jonas/programs/wireshark/run/tshark"
    _serverqlog = ""
    def __init__(self):
        print("")

    def addTestInfo(self, testlogdir: str, scenario: str, clientpars: str, serverpars: str, clientname: str, servername: str, simulation: str):
        regex = re.compile("^(?![cs][lv]_).+\.qlog")
        files = []
        for dirpath, dirnames, filenames in os.walk(testlogdir):
            for f in filenames:
                if regex.match(f):
                    files.append(os.path.join(dirpath, f))

        for qlog in files:
            self._update_file(
                qlog, 
                scenario, 
                simulation, 
                clientpars, 
                serverpars, 
                clientname, 
                servername,
                True if "client" in qlog else False
            )

    def _update_file(self, file: str, scenario: str, simulation: str, clparams: str, svparams: str, client: str, server: str, vantageclient: bool):
        newdata_file = {}
        commit = ""

        split_path = file.split(sep="/")
        sep ="/"

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
                # Fix for picoquic qlog, where extra packet outside of connection is logged
                if data.startswith('['):
                    delim = "}]"
                    split = data.split(delim)
                    del split[0]
                    data = delim.join(split)
                else:
                    delim = "]}]}"
                    split = data.split(delim)
                    split[len(split) - 1] = ""
                    data = delim.join(split)
                try:
                    data_file = json.loads(data)
                except:
                    return
            for key in data_file:
                if key != "summary":
                    newdata_file[key] = data_file[key]

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
            self._serverqlog = newpath

        with open(newpath, "w") as qlog_file:
            json.dump(newdata_file, qlog_file)

    def pcaptojson(self, logdir: str, sim: str, met_calc: MetricCalculator, isquic: bool, run: int):
        regex = re.compile("^(?![cs][lv]_).+\.pcap")
        files = []
        for dirpath, dirnames, filenames in os.walk(logdir):
            for f in filenames:
                if regex.match(f):
                    files.append(os.path.join(dirpath, f))

        sslkeyfile = logdir + "/" + "ssl-key.log"
        sep="/"
        jsonfiles = []
        for pcap in files:
            split_path = pcap.split(sep="/")
            split_path[len(split_path) - 1] = sim + "-" + split_path[len(split_path) - 1]
            split_path[len(split_path) - 1] = split_path[len(split_path) - 1].replace("pcap", "json")
            outputfile = sep.join(split_path)
            jsonfiles.append(outputfile)
            if os.path.isfile(sslkeyfile):
                cmd = self._tshark_path + " --no-duplicate-keys -r " + pcap + " -T json -o tls.keylog_file:" + sslkeyfile + " > " + outputfile
            else:
                cmd = self._tshark_path + " --no-duplicate-keys -r " + pcap + " -T json > " + outputfile
            subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            os.remove(pcap)
        if os.path.isfile(sslkeyfile):
            os.remove(sslkeyfile)

        met_calc.calculateMetrics(logdir, jsonfiles, self._serverqlog, True, isquic, sim, run)        
        self._serverqlog = ""