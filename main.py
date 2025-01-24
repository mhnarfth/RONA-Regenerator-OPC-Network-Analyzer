# main.py
"""
Main script to orchestrate optical network path analysis.
"""

import input_parser
import path_analyzer
import output_formatter

path_analyzer.REGENERATOR_REACH_THRESHOLD_KM = 1500.0

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
