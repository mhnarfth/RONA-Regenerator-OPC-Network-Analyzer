# import graphviz

# def create_pipeline_flowchart_graphviz_vertical(output_filepath="pipeline_flowchart_vertical.svg"):
#     """Generates a VERTICAL pipeline flowchart SVG using Graphviz."""

#     dot = graphviz.Digraph('pipeline_vertical', comment='Optical Network Analysis Pipeline (Vertical)',
#                            graph_attr={'rankdir': 'TB',  # Changed to Top-to-Bottom layout
#                                        'bgcolor': 'transparent',
#                                        'margin': '20', # Add margin for better spacing
#                                        'compound': 'true'}) # Enable subgraphs for clusters
#     dot.attr('node', shape='box', style='filled', fillcolor='#e0e0e0', fontname='Helvetica', fontsize='12')
#     dot.attr('edge', arrowhead='vee', arrowtail='tee', arrowsize='0.8', fontname='Helvetica', fontsize='10')

#     # Nodes
#     with dot.subgraph(name='cluster_simon', graph_attr={'label': '1. Simon Simulator', 'labelloc': 't', 'style': 'rounded, bold', 'color': 'black'}) as simon_cluster:
#         simon_cluster.node('simon_simulator', label='Simon Simulator\n(Black Box)', shape='box', style='filled', fillcolor='#f0f0f0')
#         simon_cluster.node('topology_input', label='Input:\nTopology File', shape='plaintext', fontsize='13')
#         simon_cluster.node('simon_output', label='Output:\nsimon_output_us_topology.txt', shape='plaintext', fontsize='13')

#     with dot.subgraph(name='cluster_nparc', graph_attr={'label': '2. NPARC Python Tool', 'labelloc': 't', 'style': 'rounded, bold', 'color': 'blue', 'fillcolor': '#cce0ff', 'bgcolor': '#cce0ff'}) as nparc_cluster:
#         nparc_cluster.attr('node', shape='box', style='filled', fillcolor='#cce0ff')
#         nparc_cluster.node('input_parser', label='2a. Input Parser\n(input_parser.py)')
#         nparc_cluster.node('path_analyzer', label='2b. Path Analyzer\n(path_analyzer.py)')
#         nparc_cluster.node('output_formatter', label='2c. Output Formatter\n(output_formatter.py)')
#         nparc_cluster.node('parsed_data', label='Parsed Path Data', shape='plaintext', fontsize='13')
#         nparc_cluster.node('analysis_data', label='Analysis Results', shape='plaintext', fontsize='13')
#         nparc_cluster.node('csv_data', label='Formatted CSV Data', shape='plaintext', fontsize='13')


#     with dot.subgraph(name='cluster_csv_output', graph_attr={'label': '3. CSV Output File', 'labelloc': 't', 'style': 'rounded, bold', 'color': 'black'}) as csv_cluster:
#         csv_cluster.node('csv_file_output', label='CSV Output File\npath_analysis_output.csv', shape='box', style='filled', fillcolor='#ccffcc')
#         csv_cluster.node('analysis_results_label', label='Analysis Results', shape='plaintext', fontsize='13')


#     # Edges (Data Flow) - Adjusted for Vertical Layout - Simpler Connections
#     dot.edge('topology_input', 'simon_simulator', label='Topology Data', style='dashed', color='black')
#     dot.edge('simon_simulator', 'simon_output', style='solid', color='black')
#     dot.edge('simon_output', 'input_parser', label='Simon Output\n(simon_output_us_topology.txt)')
#     dot.edge('input_parser', 'parsed_data', label='Parsed Path Data')
#     dot.edge('parsed_data', 'path_analyzer', label='Parsed Data')
#     dot.edge('path_analyzer', 'analysis_data', label='Analysis Results')
#     dot.edge('analysis_data', 'output_formatter', label='Analysis Data')
#     dot.edge('output_formatter', 'csv_data', label='Formatted CSV Data')
#     dot.edge('csv_data', 'csv_file_output', label='Contains', style='dashed', color='black')


#     dot.render(output_filepath, view=False, format='svg') # Generate SVG file
#     print(f"Vertical Flowchart SVG saved to: {output_filepath}")


# if __name__ == '__main__':
#     create_pipeline_flowchart_graphviz_vertical()



import graphviz

def create_vertical_pipeline_flowchart_graphviz_refined(output_filepath="pipeline_flowchart_vertical_refined.svg"):
    """Generates a refined vertical pipeline flowchart SVG using Graphviz with spacing adjustments."""

    dot = graphviz.Digraph('vertical_pipeline_refined', comment='Refined Vertical Optical Network Analysis Pipeline',
                           graph_attr={'rankdir': 'TB', 'bgcolor': 'transparent', 'compound': 'true', 'nodesep': '0.6', 'ranksep': '0.8'}) # Increased ranksep and nodesep for spacing

    dot.attr('node', shape='box', style='filled', fillcolor='#e0e0e0', fontname='Helvetica', fontsize='12', margin='0.1,0.1') # Reduced node margin slightly
    dot.attr('edge', arrowhead='vee', arrowtail='tee', arrowsize='0.7', fontname='Helvetica', fontsize='10', minlen='1.5') # Increased minlen for longer arrows

    # 1. Simon Simulator Box (Vertical Top)
    with dot.subgraph(name='cluster_simon', graph_attr={'label': '1. Simon Simulator', 'labelloc': 't', 'style': 'rounded, bold', 'color': 'black'}) as simon_cluster:
        simon_cluster.attr(rankdir='LR')
        simon_cluster.node('topology_input', label='Input:\nTopology File', shape='plaintext', fontsize='13')
        simon_cluster.node('simon_simulator', label='Simon Simulator\n(Black Box)', fillcolor='#f0f0f0')
        simon_cluster.node('simon_output', label='Output:\nsimon_output_us_topology.txt', shape='plaintext', fontsize='13')
        simon_cluster.edge('topology_input', 'simon_simulator', label='Topology Data', style='dashed', color='black')
        simon_cluster.edge('simon_simulator', 'simon_output', style='solid', color='black', minlen='1') # Reduced minlen here


    # 2. NPARC Python Tool Box (Vertical Middle)
    with dot.subgraph(name='cluster_nparc', graph_attr={'label': '2. NPARC Python Tool', 'labelloc': 't', 'style': 'rounded, bold', 'color': 'blue', 'fillcolor': '#cce0ff', 'bgcolor': '#cce0ff'}) as nparc_cluster:
        nparc_cluster.attr(rankdir='LR')
        nparc_cluster.attr('node', shape='box', style='filled', fillcolor='#cce0ff')
        nparc_cluster.node('input_parser', label='2a. Input Parser\n(input_parser.py)')
        nparc_cluster.node('path_analyzer', label='2b. Path Analyzer\n(path_analyzer.py)')
        nparc_cluster.node('output_formatter', label='2c. Output Formatter\n(output_formatter.py)')
        nparc_cluster.node('parsed_data', label='Parsed Path Data', shape='plaintext', fontsize='13', group='nparc_data')
        nparc_cluster.node('analysis_data', label='Analysis Results', shape='plaintext', fontsize='13', group='nparc_data')
        nparc_cluster.node('csv_data_internal', label='Formatted CSV Data', shape='plaintext', fontsize='13', group='nparc_data')


        nparc_cluster.edge('input_parser', 'parsed_data', label='Parsed Path Data', class_='arrow-label', minlen='1') # Reduced minlen here
        nparc_cluster.edge('parsed_data', 'path_analyzer', label='Parsed Data', class_='arrow-label', minlen='1') # Reduced minlen here
        nparc_cluster.edge('path_analyzer', 'analysis_data', label='Analysis Results', class_='arrow-label', minlen='1') # Reduced minlen here
        nparc_cluster.edge('analysis_data', 'output_formatter', label='Analysis Data', class_='arrow-label', minlen='1') # Reduced minlen here
        nparc_cluster.edge('output_formatter', 'csv_data_internal', label='Formatted CSV Data', class_='arrow-label', minlen='1') # Reduced minlen here


    # 3. CSV Output File Box (Vertical Bottom - nudged right)
    with dot.subgraph(name='cluster_csv_output', graph_attr={'label': '3. CSV Output File', 'labelloc': 't', 'style': 'rounded, bold', 'color': 'black', 'x': '1.2', 'rank': 'same'}) as csv_cluster: # rank:same to align horizontally, x: nudge right
        csv_cluster.attr(rankdir='LR')
        csv_cluster.node('csv_file_output', label='CSV Output File\npath_analysis_output.csv', shape='box', style='filled', fillcolor='#ccffcc')
        csv_cluster.node('analysis_results_label', label='Analysis Results', shape='plaintext', fontsize='13')
        csv_cluster.edge('csv_file_output', 'analysis_results_label', style='dashed', color='black', label='Contains', class_='arrow-label', minlen='1') # Reduced minlen here


    # Vertical Arrows connecting the main stages - using headport and tailport for better connection points
    dot.edge('simon_simulator', 'nparc_cluster', label='Simon Output\n(simon_output_us_topology.txt)', class_='arrow-label', tailport='s', headport='n', minlen='2') # Increased minlen for vertical arrow
    dot.edge('output_formatter', 'csv_file_output', label='Formatted CSV Data', class_='arrow-label', tailport='e', headport='w', minlen='2') # Increased minlen for vertical arrow


    dot.render(output_filepath, view=False, format='svg')
    print(f"Vertical Flowchart SVG saved to: {output_filepath}")


if __name__ == '__main__':
    create_vertical_pipeline_flowchart_graphviz_refined()