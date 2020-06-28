import sys, os, re, json
from metriccalculator import MetricCalculator

def groupMetrics(logdir: str):
    print("grouping metrics")
    metrics = []
    # get all "metrics.json" files
    metricfiles = getMetricFiles(logdir)
    # loop through files
    for mfile in metricfiles:
        mdata = open(mfile, "r")
        mdata = json.load(mdata)
        # for each entry see if it exists
        for testcase in mdata:
            mindex = next((i for i, item in enumerate(metrics) if item['name'] == testcase['name'] and item['sim'] == testcase['sim']), -1)
            # if not add entry to dict
            if mindex == -1:
                metrics.append({
                    "name": testcase['name'],
                    "sim": testcase['sim'],
                    "mdn_goodput": 0.0,
                    "mdn_throughput": 0.0,
                    "mdn_rtt": 0.0,
                    "mdn_cwnd": 0.0,
                    "mdn_rttvar": 0.0,
                    "mdn_retransmissions": 0,
                    "mdn_spurious_retrans": 0,
                    "mdn_rack_timer": 0.0,
                    "mdn_probe_timer": 0.0,
                    "mdn_retrans_timer": 0.0,
                    "runs": []
                })
                mindex = len(metrics) - 1
            # add runs to entry in dict
            runs = testcase['runs']
            metrics[mindex]['runs'].extend(runs)
    # loop through each entry
    metric_calc = MetricCalculator()
    metric_calc.addMediansToResults(metrics)
    with open(logdir + "/metrics.json", mode='w') as metrics_file:
        json.dump(metrics, metrics_file, indent=4)

def getMetricFiles(logdir: str):
    regex = re.compile("metrics.\.json")
    metricfiles = []
    # find converted pcap files
    for dirpath, dirnames, filenames in os.walk(logdir):
        for f in filenames:
            if regex.match(f):
                metricfiles.append(os.path.join(dirpath, f))
    
    return metricfiles

if len(sys.argv) < 2:
    print("insert directory name of collected log files")
    exit(0)

logdir = os.path.dirname(os.path.abspath(__file__)) + "/logs/" + sys.argv[1]

if os.path.isdir(logdir):
    groupMetrics(logdir)
else:
    print("directory does not exist")
    exit(0)