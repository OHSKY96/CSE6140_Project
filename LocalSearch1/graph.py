import os
import numpy as np
import matplotlib.pyplot as plt

def find_all_instances(folder):
    folder_path = folder 
    file_names = os.listdir(folder_path)
    file_names = [f for f in file_names if os.path.isfile(os.path.join(folder_path, f))]
    return file_names

def read_first_number(file_path):
    with open(file_path, 'r') as f:
        first_line = f.readline().strip()
        return int(first_line.split()[0])
    
def parse_trace_file(file_path):
    times = []
    qualities = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():  # Skip empty lines
                time_str, quality_str = line.strip().split()
                times.append(float(time_str))
                qualities.append(int(quality_str))
    return times, qualities

def rel_error(experiment, ls):
    return (ls-experiment)/experiment


def qrtd_plot(trace_files, thresholds,reference):
    for threshold in thresholds:
        success_times = []
        for file_path in trace_files:
            times, qualities = parse_trace_file(file_path)
            for t, q in zip(times, qualities):
                if rel_error(reference,q) <= threshold:
                    success_times.append(t)
                    break
            else:
                success_times.append(None)

        # Remove failed runs (or set to cutoff value)
        filtered = [t for t in success_times if t is not None]
        filtered.sort()

        cdf = [i / len(filtered) for i in range(1, len(filtered) + 1)]

        plt.plot(filtered, cdf, label=f'≤ {threshold}')

    plt.xlabel("Time (s)")
    plt.ylabel("Probability")
    plt.title("LS1 + QRTD: with instance "+trace_files[0].split("/")[1].split('_')[0])
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    return plt



def qr_sqd_plot(trace_files, time_points, q_opt, labels=None):
    time_points = sorted(time_points)
    results = [[] for _ in time_points]

    for file in trace_files:
        times, qualities = parse_trace_file(file)
        for i, tp in enumerate(time_points):
            best_quality = float('inf')
            for t, q in zip(times, qualities):
                if t <= tp:
                    best_quality = q
                else:
                    break
            if best_quality != float('inf'):
                rel_quality = 100 * (best_quality - q_opt) / q_opt
                results[i].append(rel_quality)

    # Plot
    for i, q_list in enumerate(results):
        if not q_list: continue
        sorted_q = np.sort(q_list)
        probs = np.arange(1, len(sorted_q) + 1) / len(sorted_q)
        label = f"{time_points[i]}s" if labels is None else labels[i]
        plt.plot(sorted_q, probs, label=label, linewidth=2)

    plt.xlabel("relative solution quality [%]")
    plt.ylabel("P(solve)")
    plt.grid(True)
    plt.legend()
    plt.title("LS1 + SQD: with instance "+trace_files[0].split("/")[1].split('_')[0])
    plt.tight_layout()
    return plt

def main():
    total = find_all_instances("Result/")
    exp = set([x.split(".")[0] for x in total])
    for i in exp:
        opt_path = "data 2/"+i.split("_")[0]+".out"
        exp_path = "Result/"+i.split(".")[0]
        reference = read_first_number(opt_path)
        ls = read_first_number(exp_path+".sol")
        time,_ = parse_trace_file(exp_path+".trace")
        print(f"{i}: runtime {time[-1]}, size {ls}, rel_err {rel_error(reference,ls)}")

def QRTD():
    total = find_all_instances("Graph/")
    exp = set(["Graph/"+x.split(".")[0]+".trace" for x in total])
    instance = set([x.split("_")[0] for x in total])
    thresholds = [0.2,0.4,0.6,0.8,1.0]
    for i in instance:
        graph = []
        opt_path = "data 2/"+i+".out"
        reference = read_first_number(opt_path)
        for j in exp:
            if j.startswith("Graph/"+i+"_"):
                graph.append(j)
            else:
                continue
        plt = qrtd_plot(graph,thresholds,reference)
        plt.savefig(f"{i}_QRTD.png")
        plt.close()

def SQD():
    total = find_all_instances("Graph/")
    exp = set(["Graph/"+x.split(".")[0]+".trace" for x in total])
    instance = set([x.split("_")[0] for x in total])
    timepoints = [2, 4,6,8,10,12]
    for i in instance:
        graph = []
        opt_path = "data 2/"+i+".out"
        reference = read_first_number(opt_path)
        for j in exp:
            if j.startswith("Graph/"+i+"_"):
                graph.append(j)
            else:
                continue
        plt = qr_sqd_plot(graph,timepoints,reference)
        plt.savefig(f"{i}_SQD.png")
        plt.close()
SQD()
QRTD()