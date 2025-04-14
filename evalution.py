# Extract results and calculate relative error

import os
import pandas as pd

def parse_sol_file(sol_path):
    '''
    Read size of solved set cover from .sol file
    Parameters:
       sol_path: file path of .sol file
    Returns:
       size of solved set cover
    '''

    try:
        with open(sol_path, 'r') as f:
            return int(f.readline().strip())
    except FileNotFoundError:
        print(f"Error: File not found at {sol_path}")
        return None

def parse_trace_file(trace_path):  # read run time from .trace file
    try:
        with open(trace_path, 'r') as f:
            lines = f.readlines()
            if lines:
                return float(lines[-1].split()[0]) #If there is multiple lines in .trace file, only use the run_time in last line
            return 0.0
    except FileNotFoundError:
        print(f"Error: File not found at {trace_path}")
        return None

def parse_opt_file(out_path):  # Read optimal size of set cover from .out file
    try:
        with open(out_path, 'r') as f:
            return int(f.readline().strip().split()[0])  # read the first line, remove '\n' and then get the size of set cover
    except FileNotFoundError:
        print(f"Error: File not found at {out_path}")
        return None

def evaluate_results(folder1, folder2,algo, cutoff):
    '''
    Calcuate relative error and output results into an excel
    Parameters:
       folder1: folder path of .sol and .trace
       folder2: folder path of .out file
       algo: algorithm used for set cover problem. it is also an identifier in .sol and .trace files
       cutoff: cutoff in .sol and .trace file
    Return:
       print results and export results into excel file
    '''

    results = []
    for file in os.listdir(folder1):
        if file.endswith(f"_{algo}_{cutoff}.sol"):
            instance = file.replace(f"_{algo}_{cutoff}.sol", "")   # Extract instance name
            sol_path = os.path.join(folder1, f"{instance}_{algo}_{cutoff}.sol") # path of .sol file
            trace_path = os.path.join(folder1, f"{instance}_{algo}_{cutoff}.trace") # path of .trace file
            out_path = os.path.join(folder2, f"{instance}.out") # path of .out file

            try:
                alg = parse_sol_file(sol_path)
                opt = parse_opt_file(out_path)
                time_used = parse_trace_file(trace_path)
                rel_err = round((alg - opt) / opt, 2)   # Calculate relative error
                time_used = round(time_used, 2)

                results.append((instance, time_used, alg, rel_err)) # save results for each test set
            except Exception as e:
                print(f"Error reading {instance}: {e}")

    return results

res_path = 'out_put'  # folder path of .sol and .trace file
opt_out_path = 'data' # folder path of .out file
algo = 'BnB'  # Algorithm used for set cover problem
cutoff = 1200

table = evaluate_results(res_path, opt_out_path, algo, cutoff)
# Convert to DataFrame
df = pd.DataFrame(table, columns=["Dataset", "Time (s)", "Collection Size", "RelErr"])

# Save to Excel
df.to_excel("evaluation_results.xlsx", index=False)

print(f"Evaluation results from {algo} algorithm")
print("Dataset | Time (s) | Collection Size | RelErr")
for row in table:
    print(f"{row[0]:8s} | {row[1]:7.2f} | {row[2]:15d} | {row[3]:.2f}")