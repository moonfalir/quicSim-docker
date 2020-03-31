import json, os, re
import subprocess

sim = os.environ["SIM"]
tshark_path = "/wiresharkbld/run/tshark"

regex = re.compile("^(?![cs][lv]_).+\.pcap")
logdir = "/logs"
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
        cmd = tshark_path + " --no-duplicate-keys -r " + pcap + " -T json -o tls.keylog_file:" + sslkeyfile + " > " + outputfile
    else:
        cmd = tshark_path + " --no-duplicate-keys -r " + pcap + " -T json > " + outputfile
    subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    os.remove(pcap)
if os.path.isfile(sslkeyfile):
    os.remove(sslkeyfile)