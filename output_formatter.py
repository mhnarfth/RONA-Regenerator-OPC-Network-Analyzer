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

