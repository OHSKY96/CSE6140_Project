import os
import time

def read_instance(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        n, m = map(int, lines[0].split())
        sets = [set(map(int, line.split()[1:])) for line in lines[1:]]
    universe = set(range(1, n + 1))
    return universe, sets

def greedy_set_cover(universe, sets):
    covered = set()
    chosen = []
    sets = list(enumerate(sets))  # (index, set)
    while covered != universe:
        best_idx, best_new = max(
            ((i, s - covered) for i, s in sets if len(s - covered) > 0),
            key=lambda x: len(x[1]),
            default=(None, set())
        )
        if best_idx is None:
            break
        chosen.append(best_idx)
        covered |= sets[best_idx][1]
    return chosen

def write_solution_file(output_path, chosen_indices):
    with open(output_path, 'w') as f:
        f.write(str(len(chosen_indices)) + "\n")
        f.write(" ".join(map(str, sorted(chosen_indices))) + "\n")

def run_all_instances(data_dir="data", output_dir="output", cutoff=600, seed=0):
    method = "Approx"
    os.makedirs(output_dir, exist_ok=True)

    for root, _, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".in"):
                instance_path = os.path.join(root, file)
                instance_name = os.path.splitext(file)[0]
                sol_name = f"{instance_name} {method} {cutoff}.sol"
                trace_name = f"{instance_name} {method} {cutoff}.trace"

                sol_path = os.path.join(output_dir, sol_name)
                trace_path = os.path.join(output_dir, trace_name)

                print(f"Running: {instance_name}")
                universe, sets = read_instance(instance_path)

                start = time.time()
                chosen = greedy_set_cover(universe, sets)
                end = time.time()

                # Write .sol file
                write_solution_file(sol_path, chosen)

                # .trace not required for Approx per project doc — skip or make empty
                with open(trace_path, 'w') as f:
                    pass  # Not required for Approx

                print(f"Done {file} in {end - start:.2f}s — solution size: {len(chosen)}")

if __name__ == "__main__":
    run_all_instances()
