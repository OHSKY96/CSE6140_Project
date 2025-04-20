import os
import time
import random

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

def greedy_set_cover(universe_size, subsets):
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

    return sorted(cover_indices)

def write_approx_solution_file(inst_name, method, cutoff, cover_indices):
    base = inst_name.replace('.in', '')
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"{base}_{method}_{cutoff}.sol")
    try:
        with open(filename, 'w') as f:
            f.write(f"{len(cover_indices)}\n")
            f.write(" ".join(map(str, cover_indices)) + "\n")
        print(f"Solution written to {filename}")
    except Exception as e:
        print(f"Error writing solution: {e}")

def run_greedy(inst_name, cutoff, seed):
    random.seed(seed)
    instance_path = os.path.join("data", inst_name)

    universe_size, subsets = parse_set_cover_instance(instance_path)
    if universe_size is None:
        return

    start_time = time.time()
    cover_indices = greedy_set_cover(universe_size, subsets)
    elapsed = time.time() - start_time

    if elapsed > cutoff:
        print(f"Warning: Execution time {elapsed:.2f}s exceeded cutoff {cutoff}s")

    write_approx_solution_file(inst_name, "Approx", cutoff, cover_indices)
