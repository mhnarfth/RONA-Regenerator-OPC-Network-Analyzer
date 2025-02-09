#!/usr/bin/env python3
"""
main.py

Example driver script:
  1) parse the input file
  2) run path analyzer
  3) output to CSV
"""

import sys
import os

import input_parser
import path_analyzer
import output_formatter

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_file> [<output_csv>]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else "path_analysis_output.csv"

    # 1) parse
    path_records = input_parser.parse_simon_output_file(input_file)

    # 2) analyze
    # Optionally adjust threshold:
    # path_analyzer.REGENERATOR_THRESHOLD = 1500.0
    results = path_analyzer.analyze_all_paths(path_records)

    # 3) write CSV
    out_dir = "output"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    out_path = os.path.join(out_dir, output_csv)
    output_formatter.write_analysis_to_csv(results, out_path)
    print(f"Analysis complete. Results in {out_path}")

if __name__ == "__main__":
    main()