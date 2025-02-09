# #!/usr/bin/env python3
# """
# path_analyzer.py

# Implements:
#   1) Regenerator placement (per the spec sheet).
#   2) OPC placement (Case 1: no regens; Case 2: with regens).
#   3) Residual distance calculation (Scenario 1 vs. Scenario 2).

# Core requirements from the spec:
#   - Regenerator threshold (default 1500 km).
#   - Never place regenerator at true source/dest or their immediate ROADMs.
#   - If entire path <= threshold, then NO regenerators needed, but we may
#     place exactly ONE OPC if 3+ ROADM nodes exist.
#   - If path is longer, place regenerators iteratively. Then place an OPC
#     in each section if that section has 3+ ROADM nodes, at the midpoint.
#   - Residual distance:
#      * No OPC => entire path if 0 regens, else last segment
#      * With OPC => sum of |left - right| for each OPC in each section.
# """

# REGENERATOR_THRESHOLD = 2000.0

# def analyze_path(path_record):
#     """
#     Given a path record of the form:
#       {
#         'source': int,
#         'destination': int,
#         'total_cost': float,
#         'nodes': [ (nodeID, distanceToNext), ..., (finalNode, 0.0) ]
#       }

#     Returns a dict with:
#       {
#         'source': ...,
#         'destination': ...,
#         'total_distance': ...,
#         'regenerators': [...],
#         'opcs': [...],
#         'residual_distance': ...,
#         'status': 'OK' or 'UNREACHABLE'
#       }
#     """

#     source = path_record['source']
#     destination = path_record['destination']
#     node_pairs = path_record['nodes']  # list of (nodeID, distToNext)
#     total_distance = sum(x[1] for x in node_pairs)

#     # Build arrays for convenience
#     nodeIDs   = [x[0] for x in node_pairs]
#     distances = [x[1] for x in node_pairs]  # distance from nodeIDs[i] to nodeIDs[i+1]
#     n = len(nodeIDs)

#     # We define "valid" indexes for regenerators or OPC:
#     #  skip index=0 => true source
#     #  skip index=1 => source ROADM
#     #  skip index=n-2 => destination ROADM
#     #  skip index=n-1 => true destination
#     def is_valid_index(i):
#         return (2 <= i <= (n - 3))

#     # ----------------------------------------------------------------------
#     # 1) Regenerator Placement
#     # ----------------------------------------------------------------------
#     # The logic:
#     #  - If total_distance <= threshold, then we have 0 regenerators. Done.
#     #    (But keep going for the OPC logic.)
#     #  - Else, we iteratively track cumulative distance from the "last" reg
#     #    (initially from nodeIDs[0]) and if adding distances[i-1] overshoots
#     #    threshold, we place a reg at nodeIDs[i-1] (if valid).
#     #  - If not valid => unreachable.

#     regens = []
#     unreachable = False

#     if total_distance <= REGENERATOR_THRESHOLD:
#         # "No Regenerators Needed" case from spec
#         # do nothing special, regens = []
#         pass
#     else:
#         # iterative approach
#         local_dist = 0.0
#         for i in range(1, n):
#             # add link from i-1 -> i
#             dist_incr = distances[i-1]
#             local_dist += dist_incr
#             if local_dist > REGENERATOR_THRESHOLD:
#                 # place a reg at i-1 if valid
#                 if not is_valid_index(i-1):
#                     unreachable = True
#                     break
#                 regens.append(nodeIDs[i-1])
#                 # reset local_dist
#                 local_dist = dist_incr
#                 if local_dist > REGENERATOR_THRESHOLD:
#                     unreachable = True
#                     break

#     if unreachable:
#         return {
#             'source': source,
#             'destination': destination,
#             'total_distance': round(total_distance,2),
#             'regenerators': [],
#             'opcs': [],
#             'residual_distance': 0.0,
#             'status': 'UNREACHABLE'
#         }

#     # ----------------------------------------------------------------------
#     # 2) OPC Placement
#     # ----------------------------------------------------------------------
#     # According to the spec:
#     #
#     # Case 1: No Regenerators on Path
#     #  - Condition: total_dist <= threshold
#     #  - If the path has 3 or more ROADM nodes (counting the two ROADMs
#     #    connected to source/destination, but not the true source/dest),
#     #    place exactly 1 OPC at the midpoint.
#     #
#     # Case 2: Regenerators Placed on Path
#     #  - Break path into sections: (source -> R1), (R1->R2), ..., (Rk->destination).
#     #  - If a section has 3 or more ROADM nodes, place 1 OPC at the
#     #    node nearest the midpoint. Skip source/dest + their immediate ROADMs.
#     #
#     # "3 or more ROADM nodes" means in that section's node list, if we
#     #  exclude the "true source" and "true destination" but DO include their
#     #  ROADMs, we need count >= 3.
#     # ----------------------------------------------------------------------
#     opcs = []

#     # Helper: to build partial sums for the entire path
#     # partial_sums[i] => distance from nodeIDs[0] to nodeIDs[i]
#     partial_sums = [0.0]*n
#     accum = 0.0
#     for i in range(1, n):
#         accum += distances[i-1]
#         partial_sums[i] = accum

#     def section_distance(start_i, end_i):
#         """Distance from nodeIDs[start_i] to nodeIDs[end_i]."""
#         return abs(partial_sums[end_i] - partial_sums[start_i])

#     # define a small function to place exactly one OPC at midpoint of
#     # a sub-section [start_i..end_i], if that sub-section has >= 3 "ROADM nodes."
#     # We'll skip the spec's excluded nodes for the actual placement.
#     def place_one_opc_in_section(start_i, end_i):
#         """
#         Returns a single nodeID or None if no suitable node.
#         We find the node in the interior that's closest to the midpoint.
#         The sub-section distance is partial_sums[end_i] - partial_sums[start_i].
#         """
#         dist_sec = section_distance(start_i, end_i)
#         if dist_sec <= 0:
#             return None
#         # # of sub-section nodes
#         count_sub = (end_i - start_i + 1)
#         if count_sub < 3:
#             return None
#         midpoint_val = partial_sums[start_i] + (dist_sec/2.0)

#         best_idx = None
#         best_diff= 1e15
#         # interior => range(start_i+1, end_i)
#         for idx in range(start_i+1, end_i):
#             if not is_valid_index(idx):
#                 continue
#             # cumulative distance at idx
#             cd = partial_sums[idx]
#             diff = abs(cd - midpoint_val)
#             if diff < best_diff:
#                 best_diff = diff
#                 best_idx = idx

#         if best_idx is not None:
#             return nodeIDs[best_idx]
#         else:
#             return None

#     if len(regens) == 0:
#         # => either total_distance <= threshold or path is large but we never triggered a reg
#         # from spec: "No Regenerators on Path" => place 1 OPC if path <= threshold AND we
#         # have 3 or more ROADM nodes (including source & dest ROADMs).
#         if total_distance <= REGENERATOR_THRESHOLD:
#             # Let's count how many "ROADM nodes" we have:
#             # By definition, we skip true source (index=0) & true destination (index=n-1),
#             # but we do include indices=1..(n-2) in the count. If that count >=3, place 1 OPC.
#             # Actually the spec says: "if the path has 3 or more ROADM nodes (including the Source
#             # and Destination ROADMs)". That basically means if (n >= 4?), but let's be strict:
#             #   Because n is the total # of nodes (source + srcROADM + ... + destROADM + dest).
#             # If n >= 4, we have at least [0,1,...,n-2,n-1].
#             # We specifically want to see if there's at least 3 in [0..n-1] excluding the real ends => i.e. n-2 >= 2 => n>=4
#             # But the spec also says "we exclude the true source and destination nodes" from the final count.
#             # So the "internal" list is [1..(n-2)] for counting. If len(1..n-2) >= 3 => place OPC
#             if (n - 2) >= 3:
#                 # place exactly 1 OPC in the entire path: sub-section is [0..n-1].
#                 candidate_opc = place_one_opc_in_section(0, n-1)
#                 if candidate_opc is not None:
#                     opcs.append(candidate_opc)
#     else:
#         # We do "Case 2": path is broken into sub-sections: (source->reg1), (reg1->reg2),..., (regK->destination).
#         # Steps:
#         # 1) build anchor list = [0] + indices_of_regens + [n-1] (if not already included)
#         # 2) for each sub-section in anchor list, if 3 or more ROADM nodes, place 1 OPC
#         anchor_idx = [0]
#         # find the indices for each reg node
#         reg_indices = []
#         for idx, nd in enumerate(nodeIDs):
#             if nd in regens:
#                 reg_indices.append(idx)
#         reg_indices.sort()
#         anchor_idx.extend(reg_indices)
#         if (n-1) not in anchor_idx:
#             anchor_idx.append(n-1)

#         # For each sub-section
#         for i_sub in range(len(anchor_idx) - 1):
#             s_i = anchor_idx[i_sub]
#             e_i = anchor_idx[i_sub+1]
#             # place 1 OPC if that sub-section has >=3 nodes
#             # use the helper:
#             candidate_opc = place_one_opc_in_section(s_i, e_i)
#             if candidate_opc is not None:
#                 opcs.append(candidate_opc)

#     # ----------------------------------------------------------------------
#     # 3) Residual Distance Calculation
#     # ----------------------------------------------------------------------
#     # Scenario 1: No OPC => the residual is the last-segment distance from last reg to dest,
#     # or entire path if no regens.
#     # Scenario 2: Has OPC => for each OPC in each relevant section, we do
#     #   left = distance from section start to OPC
#     #   right= distance from OPC to section end
#     #   residual(OPC) = |left - right|
#     # Sum across all OPCs.
#     # ----------------------------------------------------------------------
#     if len(opcs) == 0:
#         # scenario 1 => no OPC
#         if len(regens) == 0:
#             # entire path
#             residual_dist = total_distance
#         else:
#             # from last reg to destination
#             last_reg = regens[-1]
#             last_reg_idx = nodeIDs.index(last_reg)
#             # sum from last_reg_idx to the end
#             residual_dist = 0.0
#             for k in range(last_reg_idx, n-1):
#                 residual_dist += distances[k]
#     else:
#         # scenario 2 => we have at least 1 OPC
#         # Summation of residual for each OPC, but we must do it "per section"
#         # i.e. if an OPC belongs to the section [anchor_i..anchor_i+1].
#         # We'll re-construct the anchor list exactly as in OPC placement.
#         anchor_idx = [0]
#         reg_indices = []
#         for idx, nd in enumerate(nodeIDs):
#             if nd in regens:
#                 reg_indices.append(idx)
#         reg_indices.sort()
#         anchor_idx.extend(reg_indices)
#         if (n-1) not in anchor_idx:
#             anchor_idx.append(n-1)

#         opc_set = set(opcs)
#         residual_dist = 0.0

#         # We'll examine each sub-section [start..end]. If an OPC is in the interior,
#         # we compute its left & right, add the absolute diff to total.
#         for i_sub in range(len(anchor_idx) - 1):
#             s_i = anchor_idx[i_sub]
#             e_i = anchor_idx[i_sub+1]
#             # The interior is range(s_i+1, e_i)
#             # If there's an OPC, presumably there's exactly 1 if it placed from logic above.
#             # We'll find it:
#             sub_opc = None
#             for x in range(s_i+1, e_i):
#                 if nodeIDs[x] in opc_set:
#                     sub_opc = x
#                     break
#             if sub_opc is not None:
#                 left_dist  = abs(partial_sums[sub_opc] - partial_sums[s_i])
#                 right_dist = abs(partial_sums[e_i] - partial_sums[sub_opc])
#                 residual_dist += abs(left_dist - right_dist)

#     return {
#         'source': source,
#         'destination': destination,
#         'total_distance': round(total_distance,2),
#         'regenerators': regens,
#         'opcs': opcs,
#         'residual_distance': round(residual_dist,2),
#         'status': 'OK'
#     }

# def analyze_all_paths(path_records):
#     """
#     Applies analyze_path(...) to each path dict in path_records.
#     Returns a list of analysis results.
#     """
#     out = []
#     for p in path_records:
#         out.append(analyze_path(p))
#     return out




#!/usr/bin/env python3
"""
path_analyzer.py

Implements:
  1) Regenerator placement
  2) OPC placement
  3) Residual distance calculation

Based on the spec sheet's logic:
-------------------------------------------
Regenerator Placement (threshold-based):
 - If total path <= threshold, then no regens needed.
 - Else, do iterative distance check from the source.
 - Never place a reg at the true source node, destination node,
   or their immediate ROADMs (index=0,1, n-2,n-1).
 - If we exceed threshold but can't place a reg (invalid node),
   path is unreachable.

OPC Placement:
-------------------------------------------
Case 1: No regens => if path <= threshold and
   path has >= 3 intermediate ROADM nodes, place exactly 1 OPC
Case 2: With regens => break path into sub-sections
   [source->R1], [R1->R2], ... [Rk->destination]
   If a sub-section has >= 3 nodes (excluding the real ends),
   place 1 OPC at the node nearest the midpoint.

Residual Distance:
-------------------------------------------
Scenario 1 (No OPC):
 - If no regens, entire path
 - Else from last reg to destination

Scenario 2 (One or more OPCs):
 - For each OPC, residual(OPC) = |left - right|
 - Then ADD the distance from the last regenerator to the final node.
 - Return sum of all residual(OPC) + leftover-last-segment.

"""

REGENERATOR_THRESHOLD = 1000.0

def analyze_path(path_record):
    """
    Analyzes a single path dict of the form:
      {
        'source': int,
        'destination': int,
        'nodes': [ (nodeID, distToNext), (nodeID, distToNext), ..., (finalNode,0.0) ],
        'total_cost': ...
      }

    Returns a dict with:
      {
        'source': ...,
        'destination': ...,
        'total_distance': float,
        'regenerators': [...],
        'opcs': [...],
        'residual_distance': float,
        'status': 'OK' or 'UNREACHABLE'
      }
    """

    source = path_record['source']
    destination = path_record['destination']
    node_pairs = path_record['nodes']  # list of (nodeID, distanceToNext)
    total_distance = sum(x[1] for x in node_pairs)

    # Build a nodeID list & distances array
    nodeIDs   = [x[0] for x in node_pairs]
    distances = [x[1] for x in node_pairs]  # distance from nodeIDs[i]->nodeIDs[i+1]
    n = len(nodeIDs)

    # Valid index check (skip src, src-ROADM, dest-ROADM, dest):
    # i=0 => true source
    # i=1 => source ROADM
    # i=n-2 => destination ROADM
    # i=n-1 => true destination
    def is_valid_index(i):
        return (2 <= i <= (n - 3))

    # ----------------------------------------------------------------------
    # 1) Regenerator Placement
    # ----------------------------------------------------------------------
    unreachable = False
    regens = []

    if total_distance <= REGENERATOR_THRESHOLD:
        # No regens needed
        pass
    else:
        local_dist = 0.0
        for i in range(1, n):
            dist_incr = distances[i-1]
            local_dist += dist_incr
            if local_dist > REGENERATOR_THRESHOLD:
                # place reg at i-1 if valid
                if not is_valid_index(i-1):
                    unreachable = True
                    break
                regens.append(nodeIDs[i-1])
                local_dist = dist_incr
                if local_dist > REGENERATOR_THRESHOLD:
                    unreachable = True
                    break

    if unreachable:
        return {
            'source': source,
            'destination': destination,
            'total_distance': round(total_distance,2),
            'regenerators': [],
            'opcs': [],
            'residual_distance': 0.0,
            'status': 'UNREACHABLE'
        }

    # ----------------------------------------------------------------------
    # 2) OPC Placement
    # ----------------------------------------------------------------------
    # partial sums array for distance from nodeIDs[0] to nodeIDs[i]
    partial_sums = [0.0]*n
    accum = 0.0
    for i in range(1, n):
        accum += distances[i-1]
        partial_sums[i] = accum

    def section_distance(start_i, end_i):
        return abs(partial_sums[end_i] - partial_sums[start_i])

    def place_one_opc_in_section(start_i, end_i):
        """
        Return the nodeID for the OPC placed in interior if sub-section has >=3 nodes,
        picking the node closest to midpoint. Otherwise, None.
        """
        count_sub = (end_i - start_i + 1)
        if count_sub < 3:
            return None
        sec_dist = section_distance(start_i, end_i)
        if sec_dist <= 0:
            return None
        midpoint_val = partial_sums[start_i] + sec_dist/2.0

        best_idx = None
        best_diff= 1e15
        for idx in range(start_i+1, end_i):
            if not is_valid_index(idx):
                continue
            dist_here = partial_sums[idx]
            diff = abs(dist_here - midpoint_val)
            if diff < best_diff:
                best_diff = diff
                best_idx = idx
        if best_idx is not None:
            return nodeIDs[best_idx]
        return None

    opcs = []

    if len(regens) == 0:
        # Case 1: No regens
        if total_distance <= REGENERATOR_THRESHOLD:
            # spec: place exactly 1 OPC if path has >=3 roadm nodes
            # i.e. if n >=4, we have at least 2 internal indices
            if (n-2) >= 3:
                # entire path is [0..n-1]
                c_opc = place_one_opc_in_section(0, n-1)
                if c_opc:
                    opcs.append(c_opc)
    else:
        # Case 2: With regens => break path into sub-sections
        anchor_idx = [0]
        reg_idx_list = []
        for idx, nd in enumerate(nodeIDs):
            if nd in regens:
                reg_idx_list.append(idx)
        reg_idx_list.sort()
        anchor_idx.extend(reg_idx_list)
        if (n-1) not in anchor_idx:
            anchor_idx.append(n-1)

        for i_sub in range(len(anchor_idx)-1):
            s_i = anchor_idx[i_sub]
            e_i = anchor_idx[i_sub+1]
            c_opc = place_one_opc_in_section(s_i, e_i)
            if c_opc:
                opcs.append(c_opc)

    # ----------------------------------------------------------------------
    # 3) Residual Distance
    # ----------------------------------------------------------------------
    # Scenario 1: No OPC => same as before
    # Scenario 2: >=1 OPC => sum(|L-R|) for each OPC, then ADD "last segment from last reg to final node"
    # per your request.
    # ----------------------------------------------------------------------
    if len(opcs) == 0:
        # scenario 1: no OPC
        if len(regens) == 0:
            # entire path
            residual_dist = total_distance
        else:
            # from last reg to end
            last_reg = regens[-1]
            lr_idx = nodeIDs.index(last_reg)
            leftover = 0.0
            for k in range(lr_idx, n-1):
                leftover += distances[k]
            residual_dist = leftover
    else:
        # scenario 2: we do sum of all |L-R| + leftover from last reg->destination
        # 1) sum of |L-R|
        anchor_idx = [0]
        reg_idx_list = []
        for idx, nd in enumerate(nodeIDs):
            if nd in regens:
                reg_idx_list.append(idx)
        reg_idx_list.sort()
        anchor_idx.extend(reg_idx_list)
        if (n-1) not in anchor_idx:
            anchor_idx.append(n-1)

        opc_set = set(opcs)
        sum_abs_diff = 0.0

        for i_sub in range(len(anchor_idx) - 1):
            s_i = anchor_idx[i_sub]
            e_i = anchor_idx[i_sub+1]
            # find if there's an OPC in the interior
            the_opc_idx = None
            for x in range(s_i+1, e_i):
                if nodeIDs[x] in opc_set:
                    the_opc_idx = x
                    break
            if the_opc_idx is not None:
                leftd  = abs(partial_sums[the_opc_idx] - partial_sums[s_i])
                rightd = abs(partial_sums[e_i] - partial_sums[the_opc_idx])
                sum_abs_diff += abs(leftd - rightd)

        # 2) leftover from last reg to final node
        leftover = 0.0
        if len(regens) > 0:
            last_reg = regens[-1]
            lr_idx   = nodeIDs.index(last_reg)
            for k in range(lr_idx, n-1):
                leftover += distances[k]
        else:
            # edge case: if there's an OPC but no regens, the "last segment"
            # might be entire path from source? But your example is always
            # with at least 1 reg. If needed, adapt here:
            leftover = 0.0  # or leftover = total_distance?

        residual_dist = sum_abs_diff + leftover

    return {
        'source': source,
        'destination': destination,
        'total_distance': round(total_distance,2),
        'regenerators': regens,
        'opcs': opcs,
        'residual_distance': round(residual_dist,2),
        'status': 'OK'
    }

def analyze_all_paths(path_records):
    results = []
    for p in path_records:
        results.append(analyze_path(p))
    return results