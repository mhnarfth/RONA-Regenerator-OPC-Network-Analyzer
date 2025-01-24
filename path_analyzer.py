# path_analyzer.py
"""
Module for analyzing path data to place regenerators and OPCs.
"""

REGENERATOR_REACH_THRESHOLD_KM = 1500

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

