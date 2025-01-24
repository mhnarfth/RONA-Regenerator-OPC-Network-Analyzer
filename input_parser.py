# input_parser.py 

import os
import re # Import regular expressions

def parse_simon_output_file(filepath):
    """Parses Simon output, extracts path data - ROBUST PARSING."""
    path_data = {}
    try:
        with open(filepath, 'r') as f:
            for line_number, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                try:
                    parts = line.split('(')
                    path_identifier_part = parts[0]
                    path_identifier = path_identifier_part.split('Cost:')[0].strip()

                    nodes_distances = []
                    # Use regex to find node IDs (integers) and distances (floats)
                    matches = re.findall(r'(\d+)\s+\(([\d.]+)\)', line) # Regex to find node ID and distance pairs
                    for match in matches:
                        node_id = int(match[0])
                        distance = float(match[1])
                        nodes_distances.append((node_id, distance))

                    path_data[path_identifier] = nodes_distances

                except (ValueError, IndexError, AttributeError) as e: # Added AttributeError for regex issues
                    print(f"Error parsing line {line_number}: {line} - Error: {e}")
                    continue

    except FileNotFoundError:
        print(f"Error: Simon output file not found at: {filepath}")
        return None
    return path_data

if __name__ == '__main__':
    test_filepath = "simon_output_us_topology.txt"
    if not os.path.exists(test_filepath):
        with open(test_filepath, 'w') as f:
            f.write("1->2 (Cost: 800.02) 1 (0.01) 25 (800.00) 26 (0.01) 2 (LinkCount: 3) (Half: 400.01 between 25 and 26 for 800.00 at 26)\n")
            f.write("1->3 (Cost: 1920.02) 1 (0.01) 25 (800.00) 26 (1120.00) 27 (0.01) 3 (LinkCount: 4) (Half: 960.01 between 26 and 27 for 320.00 at 26)\n")

    parsed_data = parse_simon_output_file(test_filepath)
    if parsed_data:
        print("Parsed Simon Output Data:")
        for path_id, nodes in parsed_data.items():
            print(f"Path: {path_id}")
            for node, distance in nodes:
                print(f"  Node: {node}, Distance: {distance}")
    else:
        print("Parsing failed or file not found.")