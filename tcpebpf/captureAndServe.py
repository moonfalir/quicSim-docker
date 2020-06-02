import subprocess, os, signal, time

ebpf = subprocess.Popen(["python", "/bccscripts/tcpprobe_congestion.py"])

time.sleep(2)
params = os.environ["SERVER_PARAMS"]
subprocess.run("iperf3 " + params, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

time.sleep(2)

ebpf.send_signal(signal.SIGINT)

time.sleep(2)