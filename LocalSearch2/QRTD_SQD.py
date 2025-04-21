import os
import matplotlib.pyplot as plt
import numpy as np

# ---------- tool ----------
def find_all_instances(folder):
    file_names = os.listdir(folder)
    file_names = [f for f in file_names if os.path.isfile(os.path.join(folder, f))]
    return file_names

def parse_trace_file(file_path):
    times = []
    qualities = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():
                time_str, quality_str = line.strip().split()
                times.append(float(time_str))
                qualities.append(int(quality_str))
    return times, qualities

def read_first_number(file_path):
    with open(file_path, 'r') as f:
        first_line = f.readline().strip()
        return int(first_line.split()[0])

def rel_error(opt, current):
    return (current - opt) / opt

# ---------- QRTD ----------
def qrtd_plot(trace_files, thresholds, opt_value, instance_name, save_folder):
    for threshold in thresholds:
        success_times = []
        for file_path in trace_files:
            times, qualities = parse_trace_file(file_path)
            for t, q in zip(times, qualities):
                if rel_error(opt_value, q) <= threshold:
                    success_times.append(t)
                    break
            else:
                success_times.append(None)

        filtered_times = [t for t in success_times if t is not None]
        filtered_times.sort()

        if len(filtered_times) == 0:
            continue

        cdf = [i / len(filtered_times) for i in range(1, len(filtered_times) + 1)]

        plt.plot(filtered_times, cdf, label=f'RelErr ≤ {threshold:.2f}')

    plt.xlabel('Time (s)')
    plt.ylabel('Probability')
    plt.title(f'QRTD Plot - {instance_name}')
    plt.grid(True)
    
    lines = plt.gca().get_lines()
    if any(line.get_label() and not line.get_label().startswith('_') for line in lines):
        plt.legend()
    plt.tight_layout()

    save_path = os.path.join(save_folder, f'{instance_name}_QRTD.png')
    plt.savefig(save_path)
    plt.close()
    print(f'Saved QRTD figure for {instance_name} at {save_path}')

# ---------- SQD ----------
def sqd_plot(trace_files, time_points, opt_value, instance_name, save_folder):
    results = [[] for _ in time_points]

    for file_path in trace_files:
        times, qualities = parse_trace_file(file_path)
        for i, tp in enumerate(time_points):
            best_quality = float('inf')
            for t, q in zip(times, qualities):
                if t <= tp:
                    best_quality = q
                else:
                    break
            if best_quality != float('inf'):
                rel_quality = 100 * (best_quality - opt_value) / opt_value
                results[i].append(rel_quality)

    for i, rel_qualities in enumerate(results):
        if not rel_qualities:
            continue
        sorted_q = np.sort(rel_qualities)
        probs = np.arange(1, len(sorted_q) + 1) / len(sorted_q)
        plt.plot(sorted_q, probs, label=f"{time_points[i]}s", linewidth=2)

    plt.xlabel('Relative Solution Quality [%]')
    plt.ylabel('P(solve)')
    plt.title(f'SQD Plot - {instance_name}')
    plt.grid(True)
    
    lines = plt.gca().get_lines()
    if any(line.get_label() and not line.get_label().startswith('_') for line in lines):
        plt.legend()

    plt.tight_layout()

    save_path = os.path.join(save_folder, f'{instance_name}_SQD.png')
    plt.savefig(save_path)
    plt.close()
    print(f'Saved SQD figure for {instance_name} at {save_path}')

def main():
    result_folder      = 'Result_Sol_Trace'
    output_folder_qrtd = 'QRTD_Figures'
    output_folder_sqd  = 'SQD_Figures'

    os.makedirs(output_folder_qrtd, exist_ok=True)
    os.makedirs(output_folder_sqd,  exist_ok=True)

    instances_to_plot = ['large1', 'large10']

    default_thresholds = [0.01, 0.05, 0.1, 0.2, 0.4]

    threshold_map = {
        'large1' : [0.2, 0.4, 0.6, 0.8, 1.0],   
        'large10': [0.2, 0.4, 0.6, 0.8, 1.0]   
    }

    time_points = [0.35, 0.4, 0.45, 0.5, 0.55, 0.6]   # SQD 

    total_files = find_all_instances(result_folder)
    trace_files = [f for f in total_files if f.endswith('.trace')]

    for inst in instances_to_plot:
        instance_traces = [os.path.join(result_folder, f)
                           for f in trace_files if f.startswith(inst + '_')]
        if not instance_traces:
            print(f'Warning: no trace files for {inst}')
            continue

        opt_path = os.path.join('data', f'{inst}.out')
        if not os.path.exists(opt_path):
            print(f'Error: OPT file missing: {opt_path}')
            continue
        opt_val = read_first_number(opt_path)

        thresholds = threshold_map.get(inst, default_thresholds)

        qrtd_plot(instance_traces, thresholds, opt_val, inst, output_folder_qrtd)
        sqd_plot (instance_traces, time_points,  opt_val, inst, output_folder_sqd)

if __name__ == "__main__":
    main()
