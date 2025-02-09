#!/usr/bin/env python3
"""
output_formatter.py

Takes the final results from path_analyzer and writes them to CSV.
"""

import csv

def write_analysis_to_csv(results_list, output_csv_path):
    """
    results_list is a list of dicts of the form:
      {
        'source': int,
        'destination': int,
        'total_distance': float,
        'regenerators': [ ... ],
        'opcs': [ ... ],
        'residual_distance': float,
        'status': str
      }
    """
    fieldnames = [
        'source',
        'destination',
        'total_distance',
        'regenerators',
        'opcs',
        'residual_distance',
        'status'
    ]
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results_list:
            outrow = {
                'source': row['source'],
                'destination': row['destination'],
                'total_distance': row['total_distance'],
                'regenerators': ";".join(map(str, row['regenerators'])),
                'opcs': ";".join(map(str, row['opcs'])),
                'residual_distance': row['residual_distance'],
                'status': row['status']
            }
            writer.writerow(outrow)