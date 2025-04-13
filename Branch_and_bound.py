# This file provides codes of branch_and_bound algorithm for minimum set cover problem
# Regarding as initial upper bound, it is calculated by greedy algorithm
# The low bound for Union U and subsets Si is calculated by fractional greedy bound


from typing import List, Set, Tuple
import heapq
import time
import os


def initial_upper_bound(universe, subsets):
    '''
    Calculate the initial_upper_bound by greedy algorithm. Choose the subset with most uncovered elements in subset of
    universe each time.
    :param universe: Initial union
    :param subsets: subsets provided by inputs
    :return: number of subsets for set cover by greedy algorithm and the corresponding set cover
    '''

    uncovered = set(universe)
    selected = []
    used_indices = set()

    while uncovered:
        best_index, best_res = max(
            ((i, s) for i, s in enumerate(subsets) if i not in used_indices),
            key=lambda x: len(x[1] & uncovered),
            default=(None, set())
        )
        if not best_res:
            return float('inf'), []
        uncovered -= best_res
        used_indices.add(best_index)
        selected.append(best_index)
    return len(selected), selected



def fractional_lower_bound(uncovered, subsets):
    '''
    Calculate the lower_bound in each node. The LB = current_count + lb with/without Si in set cover.
    :param uncovered: uncovered is the difference set between U and subset Si
    :param subsets: remaining subsets
    :return: return the lower_bound for each node
    '''
    uncovered = set(uncovered)
    sets = [s & uncovered for s in subsets if s & uncovered]
    count = 0.0

    #best = max(sets, key=lambda s: len(s), default=None)
    #count = len(uncovered) / len(best)


    while uncovered:
        # Pick the set covering the most uncovered elements

        greedy_set = None
        max_size = 0

        for s in sets:  # Greedily find the subset containing most uncovered elements of universe-best_set
            if len(s) > max_size:
                max_size = len(s)
                greedy_set = s

        if not greedy_set:
            return float('inf')  # No set cover exists
        covered = len(greedy_set)
        count += 1.0 / covered  # Add a fraction to count as low-bound
        uncovered -= greedy_set
        sets = [s & uncovered for s in subsets if s & uncovered]


    return count


def branch_and_bound(universe, subsets, cutoff_time):
    '''
    Implement the branch_and_bound algorithm with initial upper bound and iteratively updated low bound. Prune some
    some branches if their low bound is bigger than current upper bound.
    '''

    start_time = time.time()  # start counting the time
    #trace_log = []

    queue = []
    # initial_UB = initial_upper_bound(universe, subsets)
    # best_res = (initial_UB, [])
    best_cost, best_subsets = initial_upper_bound(universe, subsets)  # Initial upper bound
    best_res = (best_cost, best_subsets)
    trace_log = [(0.00, best_cost)]
    #best_res = (float('inf'), [])  # record the number and subsets of set cover

    # Create a priority queue for (total_estimated_count, current_count, index, uncovered, selected subsets)
    heapq.heappush(queue, (0, 0, 0, universe, []))

    while queue:

        now = time.time()
        elapsed = now - start_time

        est_total, current_count, index, uncovered, selected = heapq.heappop(queue)

        #stop if out of time
        if elapsed > cutoff_time:
            break

        if not uncovered:   # leaf node check
            if current_count < best_res[0]:  # update results if new result is less than recorded best result （best_res)
                best_res = (current_count, selected)
                trace_log.append((elapsed, current_count))  # record new best
            continue

        if index >= len(subsets) or current_count >= best_res[0]: # Check the condition where no set cover exists
            continue

        # Include subset[index]
        new_uncovered = uncovered - subsets[index]
        lb = fractional_lower_bound(new_uncovered, subsets[index + 1:])
        est_cost = current_count + 1 + lb
        if est_cost < best_res[0]:
            heapq.heappush(queue, (est_cost, current_count + 1, index + 1, new_uncovered, selected + [index+1]))

        # Exclude subset[index]
        lb = fractional_lower_bound(uncovered, subsets[index + 1:])
        est_cost = current_count + lb
        if est_cost < best_res[0]:
            heapq.heappush(queue, (est_cost, current_count, index + 1, uncovered, selected))

    return best_res, trace_log


def parse_input_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    n, m = map(int, lines[0].split())
    U = set(range(1, n + 1))
    S = []

    for line in lines[1:1 + m]:
        parts = list(map(int, line.split()))
        subset = set(parts[1:])  # Skip the first number (subset size)
        S.append(subset)

    return U, S



def write_BnB_solution_file(instance_name, cutoff, best_solution):
    filename = f"{instance_name}_BnB_{cutoff}.sol"
    with open(filename, 'w') as f:
        f.write(f"{best_solution[0]}\n")                     # Line 1: cost
        f.write(' '.join(map(str, best_solution[1])) + '\n') # Line 2: subset indices

def write_BnB_trace_file(instance_name, cutoff, trace_log):
    filename = f"{instance_name}_BnB_{cutoff}.trace"
    with open(filename, 'w') as f:
        for timestamp, quality in trace_log:
            f.write(f"{timestamp:.6f} {quality}\n")


if __name__ == "__main__":
    cutoff_time = 1200
    for filename in os.listdir("data1"):
        if filename.endswith(".in"):
            instance_name = filename.split('.')[0]  # remove extension
            U, S = parse_input_file(f'data/{filename}')

            #U, S = parse_input_file('data/large9.in')
            best_solution, trace_log = branch_and_bound(U, S, cutoff_time )
            #print(best_solution)

            write_BnB_solution_file(instance_name, cutoff_time, best_solution)
            write_BnB_trace_file(instance_name, cutoff_time, trace_log)


