import argparse
from Branch_and_bound import *
from LocalSearch_SA import run_LS1

def parse_set_cover_instance(filename):
    """
    Parses the input file for the Set Cover instance.
    Args:
        filename (str): The path to the input .in file.
    Returns:
        tuple: (universe_size, subsets)
               - universe_size (int): Number of elements in the universe (n).
               - subsets (list): A list of sets, where each set contains the elements
                                 it covers. Indices correspond to the subset index + 1.
    """
    subsets = []
    universe_size = 0
    num_subsets = 0

    try:
        with open(filename, 'r') as f:
            # Read the first line: n m
            line1 = f.readline().strip().split()
            if len(line1) == 2:
                universe_size = int(line1[0])
                num_subsets = int(line1[1])
            else:
                 print(f"Error: First line format incorrect in {filename}")
                 return None, None

            # Read subsequent lines for subsets
            for i in range(num_subsets): # Use index i for subset number
                 line = f.readline().strip().split()
                 # First element is size |Si|, rest are elements
                 # Convert elements to integers, handle potential errors
                 try:
                      if not line: # Handle empty lines if they occur
                          print(f"Warning: Empty line {i+2} encountered in {filename}")
                          continue
                      # Expecting size followed by elements
                      # size = int(line[0]) # We don't strictly need the size, just the elements
                      elements = set(map(int, line[1:]))
                      subsets.append(elements)
                 except (ValueError, IndexError) as e:
                      print(f"Error parsing subset line {i+2} in {filename}: {e}. Line content: '{' '.join(line)}'")
                      return None, None # Abort parsing on error


        # Basic validation
        if len(subsets) != num_subsets:
             # This might trigger if empty lines were skipped, adjust logic if needed
             print(f"Warning: Mismatch between expected ({num_subsets}) and read ({len(subsets)}) subsets in {filename}")
             # Decide if this is critical; for now, allow continuing

        return universe_size, subsets
    except FileNotFoundError:
        print(f"Error: Input file not found: {filename}")
        return None, None
    except Exception as e:
        print(f"Error parsing file {filename}: {e}")
        return None, None


def main():
    parser = argparse.ArgumentParser(description="Minimum Set Cover Problem")  # Read the command line inputs

    parser.add_argument('-inst', type=str, required=True, help='Filename of the dataset')
    parser.add_argument('-alg', type=str, choices=['BnB', 'Approx', 'LS1', 'LS2'], required=True, help='Algorithm to use')
    parser.add_argument('-time', type=int, required=True, help='Cutoff time in seconds')
    parser.add_argument('-seed', type=int, required=True, help='Random seed')

    args = parser.parse_args()

    if args.alg == "BnB":
        instance = f'data/{args.inst}'  # join the folder path and instance name, like data/test1.in
        #print(instance)
        universe, subsets  = parse_set_cover_instance(instance)  # get set cover size the subsets from .in file
        universe = set(range(1, universe + 1))
        best_solution, trace_log = run_branch_and_bound(universe, subsets, args.time) # run branch_and_bound method

        # print(best_solution)
        write_BnB_solution_file(args.inst, args.time, best_solution) # write .sol file
        write_BnB_trace_file(args.inst, args.time, trace_log) # write .trace file

    elif args.alg == "Approx":
        print("Approximation algorithm not implemented yet.")

    elif args.alg == "LS1":
        run_LS1(args.inst, args.time, args.seed)
        # print("Local search algorithm not implemented yet.")
    
    elif args.alg == "LS2":
        # run_LS2(args.inst, args.time, args.seed)
        print("Local search algorithm not implemented yet.")
    else:
        print("Unknown algorithm.")

if __name__ == "__main__":
    main()



