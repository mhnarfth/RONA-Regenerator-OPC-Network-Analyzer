# NPARC: Network Path Analyzer for Regeneration and Conjugation

**NPARC** is a Python-based tool for analyzing optical network paths and determining optimal placements for **Regenerators** and **Optical Phase Conjugators (OPCs)**. The tool also calculates the **residual uncompensated dispersion distance** based on a user-defined threshold. NPARC is composed of multiple Python modules, each handling a distinct step in the pipeline.

## Table of Contents

- [Overview](#overview)  
- [Directory Structure](#directory-structure)  
- [Installation](#installation)  
- [Usage](#usage)  
- [Key Modules](#key-modules)  
- [Configuration](#configuration)  
- [Sample Workflow](#sample-workflow)  
- [Contact](#contact)

---

## Overview

Modern optical networks rely on signal regeneration at various nodes to maintain signal integrity over long distances. Optical Phase Conjugators (OPCs) can further mitigate dispersion issues. **NPARC** automates:

1. **Regenerator Placement**  
     
   - Iterative threshold checks to place regenerators on valid intermediate nodes (excluding true source/destination and their immediate ROADMs).

   

2. **OPC Placement**  
     
   - Case 1: No regenerators needed → place exactly one OPC if there are enough intermediate ROADMs.  
   - Case 2: If regenerators exist → split path into sub-sections and place one OPC per eligible section.

   

3. **Residual Distance Calculation**  
     
   - Scenario 1 (No OPC): Entire path (if no regenerators) or the last segment from the last regenerator to the destination node.  
   - Scenario 2 (With OPC): Sum of the absolute difference in left-right segments for each OPC, plus any leftover distance (e.g. from last regenerator to final node).

**Special Note**:  
This project **excludes** the true source and true destination from distance calculations. All threshold checks, regenerator placements, and residual distance computations are done between the **source ROADM** and **destination ROADM** only, ignoring small (e.g., 0.01 km) links at the path’s extremes.

---

## Directory Structure

A typical directory layout (after creation):

nparc\_project/

├── main.py

├── input\_parser.py

├── path\_analyzer.py

├── output\_formatter.py

├── simon\_output\_us\_topology.txt

├── README.md

└── output/

    └── path\_analysis\_output.csv

- **`main.py`** — The primary driver script.  
- **`input_parser.py`** — Parses the “black box” Simon output into structured path records.  
- **`path_analyzer.py`** — Contains the core regenerator/OPC placement and residual distance logic.  
- **`output_formatter.py`** — Exports results to CSV.  
- **`simon_output_us_topology.txt`** — Example input file from the Simon simulator.  
- **`output/`** — Stores generated CSV output.

---

## Installation

1. **Clone or Download** this repository.  
2. **Install Python 3.7+** (or a suitable version that supports your environment).  
3. (Optional) Create and activate a virtual environment:  
     
   python \-m venv venv  
     
   source venv/bin/activate  
     
4. (Optional) Install additional dependencies if listed in a `requirements.txt` file:  
     
   pip install \-r requirements.txt

---

## Usage

1. **Prepare your input file** (e.g., `simon_output_us_topology.txt`) in the same directory.  
2. **Run**:  
     
   cd nparc\_project  
     
   python main.py simon\_output\_us\_topology.txt  
     
   - This produces a CSV in `output/path_analysis_output.csv` by default.  
   - If you prefer a custom output file name:  
       
     python main.py simon\_output\_us\_topology.txt custom\_output.csv

     
3. Check `output/` for the CSV results.

---

## Key Modules

1. **`input_parser.py`**  
     
   - **Parses** each line of the Simon simulator’s text output.  
   - Produces a list of “path records,” where each path record includes:  
     - `source`, `destination`, `total_cost`  
     - `nodes`: a list of `(nodeID, distanceToNext)` pairs

   

2. **`path_analyzer.py`**  
     
   - **Core** of the logic:  
     - **Regenerator Placement**: Checks cumulative distance within the source-ROADM to destination-ROADM sub-array.  
     - **OPC Placement**: Places a single OPC per path (if no regenerators) or per sub-section (if regenerators exist).  
     - **Residual Distance**: Summarizes the uncompensated distance either from last regenerator or via the sum of absolute left-right differences (if OPCs exist) **plus** leftover segment.  
   - **Skips** the true source (index=0) and true destination (index=n-1).  
   - Also excludes reg/OPC from the immediate ROADMs (sub-array index=0 and index=(n-1) within the shortened path).

   

3. **`output_formatter.py`**  
     
   - Takes the final list of analysis results and **writes** them to CSV.  
   - Each row includes source, destination, total\_distance, regenerator list, OPC list, residual\_distance, and status.

   

4. **`main.py`**  
     
   - Orchestrates the steps:  
     1. Parse the input file.  
     2. Run path analysis.  
     3. Format results as CSV.

---

## Configuration

- **Global Regenerator Threshold**:  
  In `path_analyzer.py`, you can set:  
    
  REGENERATOR\_THRESHOLD \= 1500.0  
    
  or dynamically override it in `main.py`:  
    
  import path\_analyzer  
    
  path\_analyzer.REGENERATOR\_THRESHOLD \= 2000.0  
    
- **File Paths**:  
  - `main.py` takes the first command-line argument as the input file (e.g. `simon_output_us_topology.txt`).  
  - The second argument (optional) is the output CSV file name.  
  - Generated CSVs default to the `output/` folder.

---

## Sample Workflow

1. **Edit Threshold**: If you want 2000 km instead of 1500 km, open `path_analyzer.py` or do:  
     
   import path\_analyzer  
     
   path\_analyzer.REGENERATOR\_THRESHOLD \= 2000.0  
     
2. **Run**:  
     
   python main.py simon\_output\_us\_topology.txt myresults.csv  
     
3. **Inspect** `output/myresults.csv` for columns:  
     
   - `source,destination,total_distance,regenerators,opcs,residual_distance,status`

   

4. Compare results to your known sample test cases or examine in a spreadsheet.

---

## Contact

- **Project Maintainer**: M A U Shariff  
- **Research Team**: Dr. B. Ramamurthy, B. Hu, et al.

If you encounter any issues or have additional feature requests, please open an issue or reach out via the project’s communication channels.  