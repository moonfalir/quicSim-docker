import json, os, re

class QlogManager:
    def __init__(self):
        print("")

    def addTestInfo(self, testlogdir: str, scenario: str, clientpars: str, serverpars: str, clientname: str, servername: str, simulation: str):
        regex = re.compile("^(?![cs][lv]_).+")
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
        data = {}
        with open(file, "r") as qlog_file:
            data = json.load(qlog_file)
            data["summary"] = {
                "simulation": simulation,
                "scenario": scenario,
                "client": client,
                "client_params": clparams,
                "server": server,
                "server_params": svparams
            }

        os.remove(file)
        newfilename = ""
        if vantageclient:
            newfilename = "cl_"
        else:
            newfilename = "sv_"
        newfilename += simulation + "_"
        newfilename += client + "_" + server + ".qlog"

        split_path = file.split(sep="/")
        split_path[len(split_path) - 1] = newfilename
        sep ="/"
        newpath = sep.join(split_path)

        with open(newpath, "w") as qlog_file:
            json.dump(data, qlog_file)