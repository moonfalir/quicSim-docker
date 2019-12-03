import json, os

class QlogManager:
    def __init__(self):
        print("constructor")

    def addTestInfo(self, file: str, scenario: str, simulation: str, clparams: str, svparams: str, client: str, server: str):
        print("add quant info")
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

        with open(file, "w") as qlog_file:
            json.dump(data, qlog_file)