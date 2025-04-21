#!/usr/bin/env python3
# LS2 multi‑start hill‑climbing  ——  outputs drop in Result/

import sys, time, random, os           # ←①

OUT_DIR = "Result"                     # ←① output folder
os.makedirs(OUT_DIR, exist_ok=True)    # ←②

# ---------- read input ----------
def read_input(filename):
    with open(filename) as f:
        lines = f.readlines()
    n, m = map(int, lines[0].split())
    subsets = []
    for line in lines[1:]:
        nums = list(map(int, line.split()))
        subsets.append(set(nums[1:]))          # delete first line
    U = set(range(1, n + 1))
    return U, subsets

# ---------- check if the cover set is valid ----------
def is_valid(sol, subsets, U):
    cov = set()
    for idx in sol:
        cov |= subsets[idx]
    return cov >= U

# ---------- greedy initial ----------
def initial_solution(U, subsets):
    uncovered, sol = set(U), []
    while uncovered:
        best = max(range(len(subsets)), key=lambda i: len(subsets[i] & uncovered))
        sol.append(best)
        uncovered -= subsets[best]
    return sol

# ---------- delete 1 subset neighbor ----------
def get_neighbors(sol, subsets, U):
    nei = []
    for idx in sol:
        cand = sol.copy()
        cand.remove(idx)
        if is_valid(cand, subsets, U):
            nei.append(cand)
    return nei

# ---------- one time hill‑climb ----------
def hill_climb(U, subsets, cutoff, seed, t0):
    random.seed(seed)
    cur   = initial_solution(U, subsets)
    best, best_cost = cur.copy(), len(cur)
    trace = [(time.time() - t0, best_cost)]
    fail  = 0

    while time.time() - t0 < cutoff:
        nei = get_neighbors(cur, subsets, U)
        improved = False
        for cand in nei:
            if len(cand) < len(cur):
                cur, improved = cand, True
                if len(cur) < best_cost:
                    best, best_cost = cur.copy(), len(cur)
                    trace.append((time.time() - t0, best_cost))
                break
        fail = 0 if improved else fail + 1

        # light perturbation
        if fail >= 10 and len(cur) > 1:
            rm = random.choice(cur)
            cur.remove(rm)
            uncovered = U - set().union(*[subsets[i] for i in cur])
            addable   = [i for i in range(len(subsets)) if subsets[i] & uncovered]
            if addable:
                cur.append(random.choice(addable))
            fail = 0
    return best, trace

# ---------- multi‑start ----------
def multi_start(U, subsets, cutoff, seed, k=10):
    t0 = time.time()
    best_sol, best_cost, best_trace = None, float('inf'), []
    for s in range(k):
        if time.time() - t0 > cutoff: break
        sol, tr = hill_climb(U, subsets, cutoff, seed + s, t0)
        if len(sol) < best_cost:
            best_sol, best_cost, best_trace = sol, len(sol), tr
    return best_sol, best_trace

# ---------- write file ----------
def write_solution(fname, sol):
    with open(fname, 'w') as f:
        f.write(str(len(sol)) + '\n')
        f.write(' '.join(str(i + 1) for i in sorted(sol)) + '\n')

def write_trace(fname, tr):
    with open(fname, 'w') as f:
        for t, c in tr:
            f.write(f"{t:.2f} {c}\n")

# ---------- main ----------
def main():
    args   = sys.argv
    inst   = args[args.index('-inst') + 1]
    cut    = int(args[args.index('-time') + 1])
    seed   = int(args[args.index('-seed') + 1])

    U, subsets = read_input(inst)
    sol, trace = multi_start(U, subsets, cut, seed, k=10)

    assert is_valid(sol, subsets, U), "Final solution NOT covering U!"

    base = os.path.splitext(os.path.basename(inst))[0]
    alg  = "LS2"
    write_solution(os.path.join(OUT_DIR, f"{base}_{alg}_{cut}_{seed}.sol"),   sol)   # ←③
    write_trace  (os.path.join(OUT_DIR, f"{base}_{alg}_{cut}_{seed}.trace"), trace) # ←③

if __name__ == "__main__":
    main()
