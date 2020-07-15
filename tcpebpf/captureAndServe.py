import subprocess, os, signal, time

# start eBPF capture
ebpf = subprocess.Popen(["python", "/bccscripts/tcpprobe_congestion.py"])

time.sleep(8)
params = os.environ["SERVER_PARAMS"]
# start iperf transfer
subprocess.run("iperf3 " + params, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

time.sleep(5)

# stop eBPF capture
ebpf.send_signal(signal.SIGINT)

time.sleep(2)