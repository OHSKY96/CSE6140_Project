# greedy_set_cover.py

import os
import glob
import time
import pandas as pd

# --- Helper Functions ---

def parse_set_cover_instance(filename):
    subsets = []
    universe_size = 0
    try:
        with open(filename, 'r') as f:
            line1 = f.readline().strip().split()
            universe_size = int(line1[0])
            num_subsets = int(line1[1])
            for _ in range(num_subsets):
                line = f.readline().strip().split()
                elements = set(map(int, line[1:]))
                subsets.append(elements)
        return universe_size, subsets
    except Exception as e:
        print(f"Error parsing {filename}: {e}")
        return None, None


def read_optimal_value(filename):
    try:
        with open(filename, 'r') as f:
            return int(f.readline().strip())
    except Exception:
        print(f"Warning: Cannot read optimal value from {filename}")
        return None


def write_solution_file(filename_base, method, cutoff, seed, solution_indices, quality):
    sol_filename = f"{filename_base}_{method}_{cutoff}.sol"
    try:
        with open(sol_filename, 'w') as f:
            f.write(f"{quality}\n")
            f.write(" ".join(map(str, solution_indices)) + "\n")
    except Exception as e:
        print(f"Error writing {sol_filename}: {e}")


# --- Greedy Set Cover Algorithm ---

def greedy_set_cover(universe_size, subsets):
    start_time = time.time()
    uncovered = set(range(1, universe_size + 1))
    cover_indices = []
    remaining = [(i + 1, s.copy()) for i, s in enumerate(subsets)]

    while uncovered and remaining:
        best_idx, best_set, best_i = -1, set(), -1
        max_covered = -1

        for i, (idx, subset) in enumerate(remaining):
            covered = subset & uncovered
            if len(covered) > max_covered:
                best_idx, best_set, best_i = idx, covered, i
                max_covered = len(covered)

        if max_covered <= 0:
            break

        cover_indices.append(best_idx)
        uncovered -= best_set
        remaining.pop(best_i)

    exec_time = time.time() - start_time
    return sorted(cover_indices), universe_size - len(uncovered), exec_time


# --- Runner ---

def run_experiment(data_dir, pattern, method, cutoff, seed=None):
    results = []
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    input_files = sorted(glob.glob(os.path.join(data_dir, pattern)))
    if not input_files:
        print(f"Warning: No input files for pattern {pattern}")
        return results

    for in_file in input_files:
        base = os.path.basename(in_file).replace('.in', '')
        out_file = os.path.join(data_dir, base + '.out')

        universe_size, subsets = parse_set_cover_instance(in_file)
        if universe_size is None:
            results.append({'Instance': base, 'Time': 0, 'Quality': 'Error', 'Optimal': 'N/A', 'RelErr': 'N/A', 'Method': method})
            continue

        opt_value = read_optimal_value(out_file)
        cover_indices, covered_count, exec_time = greedy_set_cover(universe_size, subsets)
        quality = len(cover_indices)

        rel_err = None
        opt_display = 'N/A'
        if opt_value is not None:
            opt_display = opt_value
            rel_err = (quality - opt_value) / float(opt_value) if opt_value > 0 else float('inf')

        sol_file_base = os.path.join(output_dir, base)
        write_solution_file(sol_file_base, method, cutoff, seed, cover_indices, quality)

        results.append({
            'Instance': base,
            'Time': exec_time,
            'Quality': quality,
            'Optimal': opt_display,
            'RelErr': rel_err,
            'CoveredElements': covered_count,
            'UniverseSize': universe_size,
            'Method': method
        })

    return results


def main():
    DATA_DIRECTORY = "data"
    CUTOFF_TIME = 600
    METHOD_NAME = "Greedy"

    all_results = []
    for pattern in ["test*.in", "small*.in", "large*.in"]:
        all_results.extend(run_experiment(DATA_DIRECTORY, pattern, METHOD_NAME, CUTOFF_TIME))

    df = pd.DataFrame(all_results)

    def format_rel_err(x):
        if x is None: return 'N/A'
        if x == float('inf'): return 'inf'
        return f"{x:.4f}"

    df['RelErr_Display'] = df['RelErr'].apply(format_rel_err)
    df['Time'] = df['Time'].apply(lambda x: f"{x:.4f}")

    summary_df = df[['Instance', 'Method', 'Time', 'Quality', 'Optimal', 'RelErr_Display']]
    output_path = os.path.join("output", "greedy_results_summary.csv")
    summary_df.to_csv(output_path, index=False)

    print("\n--- Results written to:", output_path, "---")
    print(summary_df)


if __name__ == "__main__":
    main()
