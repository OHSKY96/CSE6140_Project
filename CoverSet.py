   
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
        subsets[idx]=subset_items
    return n, m, subsets


