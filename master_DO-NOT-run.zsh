# This creates the tree w/directory and dumps all the codes

#!/bin/zsh
set -e

# --- Project Directory ---
PROJECT_DIR="optical_network_analysis_one_shot"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# --- Create Python Files ---

cat > input_parser.py <<EOF
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

EOF

cat > path_analyzer.py <<EOF
# path_analyzer.py
"""
Module for analyzing path data to place regenerators and OPCs.
"""

REGENERATOR_REACH_THRESHOLD_KM = 1000.0

def regenerator_placement(path_data, reach_threshold_km=REGENERATOR_REACH_THRESHOLD_KM):
    """Determines regenerator locations for each path."""
    regenerator_locations = []
    path_sections = []
    current_section_nodes = []
    current_distance = 0.0

    if not path_data:
        return regenerator_locations, path_sections

    current_section_nodes.append(path_data[0])

    for i in range(1, len(path_data)):
        current_node, link_distance = path_data[i]
        current_section_nodes.append(path_data[i])
        current_distance += link_distance

        if current_distance > reach_threshold_km:
            if len(current_section_nodes) > 1:
                regenerator_node, _ = current_section_nodes[-2]
                regenerator_locations.append(regenerator_node)
                path_sections.append(list(current_section_nodes[:-1]))
                current_section_nodes = [path_data[i-1], path_data[i]]
                current_distance = link_distance

    path_sections.append(list(current_section_nodes))
    refined_path_sections = []
    for section in path_sections:
        refined_path_sections.append([node for node, _ in section])

    return regenerator_locations, refined_path_sections

def opc_placement(path_sections):
    """Places OPCs midway within each path section."""
    opc_locations = []
    for section_nodes in path_sections:
        if len(section_nodes) >= 3:
            midpoint_index = len(section_nodes) // 2
            opc_node = section_nodes[midpoint_index]
            opc_locations.append(opc_node)
    return opc_locations

def residual_distance_calculation(path_sections, opc_locations, path_data_tuples):
    """Calculates residual uncompensated distance for a path."""
    total_residual_distance = 0.0
    opc_locations_set = set(opc_locations)

    section_start_index = 0
    for section_nodes in path_sections:
        section_end_index = section_start_index + len(section_nodes)
        section_path_data = path_data_tuples[section_start_index:section_end_index]
        section_opc_node_ids = [node_id for node_id in section_nodes if node_id in opc_locations_set]

        if section_opc_node_ids:
            opc_node_id = section_opc_node_ids[0]
            try:
                opc_node_index_in_section = section_nodes.index(opc_node_id)
                left_segment_distance = sum(distance for _, distance in section_path_data[:opc_node_index_in_section])
                right_segment_distance = sum(distance for _, distance in section_path_data[opc_node_index_in_section:])
                residual_distance = abs(left_segment_distance - right_segment_distance)
                total_residual_distance += residual_distance
            except ValueError:
                print(f"Warning: OPC node {opc_node_id} not found in section.")

        section_start_index = section_end_index

    return total_residual_distance

if __name__ == '__main__':
    example_path_data = [
        (1, 0.01), (25, 800.00), (26, 1120.00), (27, 320.00), (28, 0.01), (4, 0.01)
    ]

    print("\n--- Regenerator Placement Test ---")
    regenerators, sections = regenerator_placement(example_path_data)
    print("Regenerator Locations:", regenerators)
    print("Path Sections (Node IDs):", sections)

    print("\n--- OPC Placement Test ---")
    opcs = opc_placement(sections)
    print("OPC Locations:", opcs)

    print("\n--- Residual Distance Calculation Test ---")
    residual_dist = residual_distance_calculation(sections, opcs, example_path_data)
    print("Residual Distance:", residual_dist, "km")

EOF

cat > output_formatter.py <<EOF
# output_formatter.py
"""
Module for formatting and writing path analysis results to CSV.
"""

import csv

def format_path_results_csv(path_results):
    """Formats path analysis results into CSV-writable dictionaries."""
    csv_rows = []
    for path_id, result in path_results.items():
        csv_row = {
            "SourceNodeID": path_id.split("->")[0],
            "DestinationNodeID": path_id.split("->")[1],
            "RegeneratorLocations": ",".join(map(str, result["regenerator_locations"])) or "None",
            "NumberOfRegenerators": result["num_regenerators"],
            "OPCLocations": ",".join(map(str, result["opc_locations"])) or "None",
            "ResidualDistance_km": result["residual_distance"]
        }
        csv_rows.append(csv_row)
    return csv_rows

def write_csv_output(path_results, output_filepath="path_analysis_output.csv"):
    """Writes path analysis results to a CSV file."""
    if not path_results:
        print("Warning: No path results to write to CSV.")
        return

    fieldnames = path_results[0].keys()

    try:
        with open(output_filepath, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(path_results)
        print(f"Path analysis results written to: {output_filepath}")
    except Exception as e:
        print(f"Error writing to CSV file: {e}")

if __name__ == '__main__':
    example_results = {
        "1->2": {
            "regenerator_locations": [],
            "num_regenerators": 0,
            "opc_locations": [],
            "residual_distance": 0.0
        },
        "1->3": {
            "regenerator_locations": [26],
            "num_regenerators": 1,
            "opc_locations": [26],
            "residual_distance": 160.0
        }
    }

    formatted_csv_data = format_path_results_csv(example_results)
    write_csv_output(formatted_csv_data, "test_output.csv")
    print("\nCheck 'test_output.csv' for example output.")

EOF

cat > main.py <<EOF
# main.py
"""
Main script to orchestrate optical network path analysis.
"""

import input_parser
import path_analyzer
import output_formatter

path_analyzer.REGENERATOR_REACH_THRESHOLD_KM = 1000.0

def main():
    simon_output_filepath = "simon_output_us_topology.txt"
    output_csv_filepath = "path_analysis_output.csv"

    print(f"Parsing Simon output file: {simon_output_filepath}...")
    parsed_path_data_dict = input_parser.parse_simon_output_file(simon_output_filepath)

    if not parsed_path_data_dict:
        print("Error: No path data parsed. Exiting.")
        return

    path_analysis_results = {}

    print("Analyzing paths and placing regenerators/OPCs...")
    for path_id, path_data_tuples in parsed_path_data_dict.items():
        regenerator_locations, path_sections = path_analyzer.regenerator_placement(path_data_tuples)
        opc_locations = path_analyzer.opc_placement(path_sections)
        residual_distance = path_analyzer.residual_distance_calculation(path_sections, opc_locations, path_data_tuples)

        path_analysis_results[path_id] = {
            "regenerator_locations": regenerator_locations,
            "num_regenerators": len(regenerator_locations),
            "opc_locations": opc_locations,
            "residual_distance": residual_distance
        }

    print("Formatting and writing output to CSV...")
    csv_output_data = output_formatter.format_path_results_csv(path_analysis_results)
    output_formatter.write_csv_output(csv_output_data, output_csv_filepath)

    print("Path analysis complete.")
    print(f"Results are in: {output_csv_filepath}")

if __name__ == "__main__":
    main()
EOF

cat > requirements.txt <<EOF
# No external dependencies required.
EOF

cat > README.md <<EOF
# Optical Network Path Analysis Script (One-Shot - Corrected)

This script analyzes optical network paths, places regenerators/OPCs, and calculates residual dispersion.

## Usage

1.  Save `run_analysis.zsh`, `simon_output_us_topology.txt` (or your data) to the same directory.
2.  Run: `zsh run_analysis.zsh`

Output is in `path_analysis_output.csv`.

## Files

- `run_analysis.zsh`: One-shot execution script.
- `input_parser.py`, `path_analyzer.py`, `output_formatter.py`, `main.py`: Python modules.
- `requirements.txt`: Python dependencies (none).
- `README.md`: This file.
EOF

# --- Create Virtual Environment, Install, and Run (Corrected Execution) ---
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate
echo "Installing requirements (if any)..."
pip install -r requirements.txt

echo "Running Python script (main.py) correctly..."
python main.py

deactivate

echo "--- Path Analysis Completed ---"
echo "Results: ${PROJECT_DIR}/path_analysis_output.csv"