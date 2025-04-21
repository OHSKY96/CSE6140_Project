import os
import numpy as np
import matplotlib.pyplot as plt

RESULT_DIR = "Result_Sol_Trace"
DATA_DIR   = "data"
INSTANCES  = ["large1", "large10"]
CUTOFF     = 120  

def parse_trace(trace_path):
    """Read the .trace file and return the final timestamp and quality."""
    times, quals = [], []
    with open(trace_path) as f:
        for line in f:
            t, q = line.split()
            times.append(float(t))
            quals.append(int(q))
    return times[-1], quals[-1]

def read_opt(inst):
    """Read optimal value from data/<inst>.out."""
    with open(os.path.join(DATA_DIR, inst + ".out")) as f:
        return int(f.readline().split()[0])

# collect data
runtimes = {inst: [] for inst in INSTANCES}
relerrs   = {inst: [] for inst in INSTANCES}

for inst in INSTANCES:
    opt = read_opt(inst)
    prefix = f"{inst}_LS2_{CUTOFF}_"
   
    all_traces = [fn for fn in os.listdir(RESULT_DIR)
                  if fn.startswith(prefix) and fn.endswith(".trace")]
    if not all_traces:
        print(f"Warning: no trace files found for {inst}")
        continue

    for fn in all_traces:
        trace_file = os.path.join(RESULT_DIR, fn)
        sol_file   = os.path.join(RESULT_DIR, fn[:-6] + ".sol")  
        if not os.path.exists(sol_file):
            print(f"Warning: missing {sol_file}")
            continue

        t_last, q_last = parse_trace(trace_file)
        runtimes[inst].append(t_last)
        relerrs[inst].append(100 * (q_last - opt) / opt)

# prepare for plotting
labels     = INSTANCES
data_time  = [runtimes[i] for i in INSTANCES]
data_error = [relerrs[i]   for i in INSTANCES]

plt.figure(figsize=(10, 4))

# Runtime boxplot
plt.subplot(1, 2, 1)
plt.boxplot(data_time, patch_artist=True, tick_labels=labels)
plt.ylabel("Running Time (s)")
plt.title("LS2 Runtime Boxplot")
plt.grid(axis='y')

# Relative Error boxplot
plt.subplot(1, 2, 2)
plt.boxplot(data_error, patch_artist=True, tick_labels=labels)
plt.ylabel("Relative Error (%)")
plt.title("LS2 Relative Error Boxplot")
plt.grid(axis='y')

plt.tight_layout()
plt.savefig("LS2_boxplots.png", dpi=150)
plt.show()
