# This is the code for the 1st local search algorithm,
# I am using a simulated annealing local search.
# Initiate the initial guess using greedy algorithm and plus random
# selected subsets to avoid a local optimal.
# Temperature is designed to decay in a constant rate 0.99, with initial
# temperature 1000 degree.
# Use a restart process for 50 steps not getting better result.
# Neighbor selection is to find the subset with most redundancy item and that
# not exist, then add 10 random selected subsets

import numpy as np
import random
import heapq
import os
import time
import concurrent.futures



def read_data(file_path):
    """
    Reads data from a specified file and returns it as a list of lines.
    Parameters:
        file_path (str): Path to the file to be read.
    Returns:
        list[str]: List of stripped lines from the file.
    """
    try:
        with open(file_path, 'r') as file:
            data = file.readlines()
        return [line.strip() for line in data if line.strip()]
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return []


def parse_data(lines):
    """
    Parses a set cover input format from lines and returns:
    - number of items (n)
    - number of subsets (m)
    - dict of subsets (each subset is a set of integers)
    Parameters:
        lines (list[str]): Lines from the input file.
    Returns:
        n, m, list of sets
    """
    # Parse first line
    [n, m] = list(map(int, lines[0].split()))
    # Parse subsets
    subsets = {}
    for idx, line in enumerate(lines[1:1 + m], 1):
        info = list(map(int, line.split()))
        num = info[0]
        subset_items = set(info[1:])
        subsets[idx]=(subset_items)
    return n, m, subsets



def f_value(S,current_items):
    """
    Computes the f value of a solution based on the number of items covered.
    Parameters:
        m (int): Total number of subsets.
        subsets list: selected subsets.
    Returns:
        int: f value.
    """
    # Initialize f_value，with the length of subsets
    f=len(S)
    # Regularize on the redundancy and disappear items
    for i in current_items:
        if current_items[i]>1:
            f+=10*current_items[i]
        elif current_items[i]==0:
            f+=100
    return f


def check_cover(current_items):
    """
    Check if the selected subsets cover all items.
    Parameters:
        n (int): Number of items.
        subsets list: selected subsets.
    Returns:
        bool: True if all items are covered, False otherwise.
        int: uncovered items
    """
    for i in current_items:
        if current_items[i]<1:
            return False
    return True
    
def probability(f1, f2, T):
    """
    Computes the probability of accepting a worse solution.
    Parameters:
        f1 (int): f value of the current solution.
        f2 (int): f value of the new solution.
        T (float): Temperature.
    Returns:
        float: Probability of accepting the new solution.
    """
    if f2 < f1:
        return 1
    else:
        return np.exp((f1 - f2) / T)
    
def Temperature(T,T1,alpha=0.99):
    """
    Computes the new temperature.
    Parameters:
        T (float): Current temperature.
        T1 (float): Initial temperature.
        alpha (float): Cooling rate.
    Returns:
        float: New temperature.
    """
    return T * alpha

def tmp_process_smarter(subsets,S,O,current_items,item_address):
    """
    Process the subsets to get the information for the temporary solution
    Parameters:
        subsets (dict) : All the subset and stored information
        S ([int]) : Selected subset index
        O ([int]) : Not selected subset index
        current_items : Item frequency in S
        item_address : backtrace the location of a certain item
    Returns:
        uncovered_items (int): Number of uncovered items.
    """
    tmp_S, tmp_O, tmp_current_items = smart_neighbor(S,O,subsets,current_items,item_address)
    cover = check_cover(tmp_current_items)
    f = f_value(tmp_S,tmp_current_items)
    return cover,tmp_S, tmp_O, tmp_current_items, f

def smart_neighbor(S, O, subsets, current_items, item_address):
    """
    Using a smarter nerghbor strategy, sort and pop the most redundancy and the absent item,
    and add a random selected list indeces
    Parameters:
        S ([int]) : Selected subset index
        O ([int]) : Not selected subset index
        subsets (dict) : All the subset and stored information
        current_items : Item frequency in S
        item_address : backtrace the location of a certain item
    """
    heap_descending = []
    heap_ascending = []

    for i in current_items:
        heapq.heappush(heap_ascending, (current_items[i], i))
        heapq.heappush(heap_descending, (-current_items[i], i))

    neighborhood = random.sample(S + O, min(len(S+O),10))

    # Redundant: pop those that appear > 1 time
    redundancy = heapq.heappop(heap_descending)
    if redundancy[0] < -1:
        idx = redundancy[1]
        for i in item_address[idx]:
            if i in S:
                neighborhood.append(i)
                    

    # Lack: item not covered
    lack = heapq.heappop(heap_ascending)
    if lack[0] == 0:
        neighborhood=[]
        idx = lack[1]
        for i in item_address[idx]:
            if i in O:
                neighborhood.append(i)
    # Fallback if neighborhood is empty
    if not neighborhood:
        neighborhood = S + O

    select = random.choice(neighborhood)

    tmp_S = S.copy()
    tmp_O = O.copy()
    tmp_current_items = current_items.copy()

    if select in S:
        tmp_S.remove(select)
        tmp_O.append(select)
        for i in subsets[select]:
            if tmp_current_items[i]>1:
                tmp_current_items[i] -= 1
            else:
                tmp_current_items[i]=0
    else:
        tmp_O.remove(select)
        tmp_S.append(select)
        for i in subsets[select]:
            tmp_current_items[i] += 1

    return tmp_S, tmp_O, tmp_current_items


def greedy_initial_solution(n, subsets):
    """
    Find a initial solution by greedily adding the subset with the most uncovered items
    Parameters:
        n(int) : total number of items
        subsets(dictionary) : subsets[i] represent the list of numbers stored in the i-th subset
    """
    uncovered =  set(range(1, n + 1))
    S = []
    O = list(subsets.keys())
    while uncovered:
        best_idx = max(subsets, key=lambda k: len(subsets[k] & uncovered))
        S.append(best_idx)
        uncovered -= subsets[best_idx]
        O.remove(best_idx)
    return S,O

def ls_sa(m,n,subsets,T0=1000,alpha=0.99):
    """
    Doing SA local search.
    Parameters:
        m(int) : the total number of subsets
        n(int) : the total number of items
        subsets(dictionary) : subsets[i] represent the list of numbers stored in the i-th subset
        T0(int) : annealing temperature
        alpha(float) : decay rate
    """
    start_time = time.time()
    trace = {}
    # Initialize the solution
    item_address = {}
    for i in subsets:
        for j in subsets[i]:
            if j in item_address.keys():
                item_address[j].append(i)
            else:
                item_address[j]=[i]
    # Greedily find a solution
    S,O = greedy_initial_solution(n,subsets)  
    # Give a random sublist to move away from local optimal  
    S=S+random.sample(O,min(len(O),int(np.sqrt(n))))
    O = [x for x in O if x not in S]
    # Create a dictionary to store the frequency of a certain item
    current_items={}
    for i in S:
        for j in subsets[i]:
            if j in current_items.keys():
                current_items[j]+=1
            else:
                current_items[j]=1
    for i in O:
        for j in subsets[i]:
            if j not in current_items.keys():
                current_items[j]=0
    # Initiate the f value, temperature, best solution, best solution size
    f_s=f_value(S,current_items)
    T=T0
    best_S=S.copy()
    best_O=O.copy()
    best_items=current_items.copy()
    restart_count=1
    best_l = len(S)
    trace[time.time()-start_time]=best_l
    i=0
    # Do local search
    while T>5:
        tmp_count = 1
        i+=1
        cover,tmp_S, tmp_O, tmp_current_items, f = tmp_process_smarter(subsets,S,O,current_items,item_address)
        # Keep tracking the possibility of this solution, with maximum try of 10 to avoid dead lock
        while (random.random()>probability(f_s,f,T)) and tmp_count<10:
            tmp_count+=1
            cover,tmp_S, tmp_O, tmp_current_items, f = tmp_process_smarter(subsets,S,O, current_items,item_address)
        # Update the solution
        S = tmp_S
        O = tmp_O
        current_items=tmp_current_items
        f_s = f
        T=Temperature(T,T0,alpha)
        # Update the optimal subsets
        if cover:
            if len(S)<best_l:
                trace_time = time.time()-start_time
                best_S = S.copy()
                best_O=O.copy()
                best_items=current_items.copy()
                best_l = len(S)
                trace[trace_time] = best_l
        # Restart if it do not work better after 50 steps
        if len(S)>best_l:
            if restart_count==50:
                S=best_S
                O=best_O
                current_items=best_items
                restart_count=1
            else:
                restart_count+=1
    return best_S, trace

def output_solution(S, instance, method, cutoff, randSeed):
    if not os.path.exists("Result_LS1"):
        os.mkdir("Result_LS1")
    quality = len(S)
    filename = f"Result_LS1/{instance}_{method}_{cutoff}_{randSeed}.sol"
    with open(filename, "w") as f:
        f.write(f"{quality}\n")
        f.write(" ".join(map(str, S)) + "\n")
    return 0

def output_trace(trace, instance, method, cutoff, randSeed):
    if not os.path.exists("Result_LS1"):
        os.mkdir("Result_LS1")
    filename = f"Result_LS1/{instance}_{method}_{cutoff}_{randSeed}.trace"
    with open(filename, "w") as f:
        for t in sorted(trace.keys()):
            f.write(f"{t:.4f} {trace[t]}\n")
    return 0


def experiment():
    data_folder = "data 2"
    all_instances = set([f.split(".")[0] for f in os.listdir(data_folder) if os.path.isfile(os.path.join(data_folder, f))])
    randSeed=1587
    cutoff = 600 

    for i in all_instances:
        print(i)
        random.seed(randSeed)
        n,m, subsets = parse_data(read_data(f"data 2/{i}.in"))


        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(ls_sa, m, n, subsets)
            try:
                best_S,trace = future.result(timeout=cutoff)
            except concurrent.futures.TimeoutError:
                print("Timed out!")
                best_S,trace = None

        if best_S:
            output_solution(best_S,i,"LS1",cutoff,randSeed=randSeed)
            output_trace(trace,i,"LS1",cutoff,randSeed)

def run_LS1(instance, cutoff, randSeed):
    n,m, subsets = parse_data(read_data(f"data 2/{instance}"))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(ls_sa, m, n, subsets)
        try:
            best_S,trace = future.result(timeout=cutoff)
        except concurrent.futures.TimeoutError:
            print("Timed out!")
            best_S,trace = None

    if best_S:
        output_solution(best_S,instance,"LS1",cutoff,randSeed=randSeed)
        output_trace(trace,instance,"LS1",cutoff,randSeed)
