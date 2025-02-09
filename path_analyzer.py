#!/usr/bin/env python3

REGENERATOR_THRESHOLD = 2000.0

def analyze_path(path_record):
    """
    Analyze a single path, ignoring the true source (index=0 in nodeIDs)
    and the true destination (index=n-1 in nodeIDs).
    We only consider [1..n-2], i.e. from source ROADM to destination ROADM.

    Then apply:
      - Regenerator logic
      - OPC logic
      - Residual distance logic
    Returns an analysis dict.
    """

    source = path_record['source']
    destination = path_record['destination']
    node_pairs = path_record['nodes']  # [(nodeID, distToNext), ... , (finalNode,0.0)]
    full_n = len(node_pairs)
    full_nodeIDs = [x[0] for x in node_pairs]
    full_distances = [x[1] for x in node_pairs]
    total_dist_full = sum(full_distances)

    # If the path has fewer than 3 nodes total, there's no ROADM in between, trivial path
    # But the user specifically wants to skip the first and last node => sub array is [1..(full_n-2)].
    if full_n < 3:
        # There's no real analysis possible
        return {
            'source': source,
            'destination': destination,
            'total_distance': 0.0,
            'regenerators': [],
            'opcs': [],
            'residual_distance': 0.0,
            'status': 'UNREACHABLE'
        }

    # ----------------------------------------------------------------------
    # 1) Build the "analysis sub-array" => nodeIDs[1..n-2]
    #    ignoring the link from 0->1 and the link from n-2->n-1
    #    so sub_array length = (full_n - 2)
    # ----------------------------------------------------------------------
    sub_nodes = full_nodeIDs[1:(full_n - 1)]  # nodeIDs[1..(n-2)]
    sub_n = len(sub_nodes)
    # e.g. if full_n=9, sub_n=7 => indices in sub_nodes => 0..6
    # sub_nodes[0] => was full_nodeIDs[1], the "source ROADM"
    # sub_nodes[sub_n-1] => was full_nodeIDs[n-2], the "destination ROADM"

    # Next, build "sub_distances" so that sub_distances[i] is the distance from
    # sub_nodes[i] -> sub_nodes[i+1], for i in [0..(sub_n-2)].
    sub_distances = []
    for i in range(sub_n - 1):
        # sub_nodes[i] is full_nodeIDs[i+1] in the original
        # we want the distance from that node to the next => we find it in the original pairs
        # simpler approach: we'll just do a small search in the original array
        # But we can do a direct method:
        #   sub_nodes[i] = full_nodeIDs[i+1],
        #   sub_nodes[i+1] = full_nodeIDs[i+2].
        # We'll find where in full_nodeIDs is sub_nodes[i], then add that dist to sub_nodes[i+1].
        current_id = sub_nodes[i]
        next_id = sub_nodes[i+1]

        # We'll track it in the full list of node_pairs. We can do a small loop:
        dist_ij = 0.0
        for j in range(1, full_n):  # full_n is the length of the original nodeIDs
            if full_nodeIDs[j-1] == current_id and full_nodeIDs[j] == next_id:
                dist_ij = full_distances[j-1]
                break
        sub_distances.append(dist_ij)

    total_sub_distance = sum(sub_distances)

    # We'll now do all threshold-based logic on sub_nodes (length sub_n) & sub_distances.
    # The sub array's index layout:
    #   sub_nodes[0] = "source ROADM"
    #   sub_nodes[sub_n-1] = "destination ROADM"

    # We'll define a function is_valid_index(i) in sub-array context:
    # skip i=0 => source ROADM, i=sub_n-1 => destination ROADM
    def is_valid_sub_index(i):
        return (1 <= i <= (sub_n - 2))

    # ----------------------------------------------------------------------
    # 2) Regenerator Placement
    # ----------------------------------------------------------------------
    unreachable = False
    regens = []  # list of nodeIDs in sub-array
    if total_sub_distance <= REGENERATOR_THRESHOLD:
        # no regens needed
        pass
    else:
        local_dist = 0.0
        for i in range(1, sub_n):
            dist_incr = sub_distances[i-1]  # distance sub_nodes[i-1] -> sub_nodes[i]
            local_dist += dist_incr
            if local_dist > REGENERATOR_THRESHOLD:
                # place a reg at i-1 if valid
                if not is_valid_sub_index(i-1):
                    unreachable = True
                    break
                regens.append(sub_nodes[i-1])
                local_dist = dist_incr
                if local_dist > REGENERATOR_THRESHOLD:
                    unreachable = True
                    break

    if unreachable:
        return {
            'source': source,
            'destination': destination,
            'total_distance': round(total_sub_distance,2),
            'regenerators': [],
            'opcs': [],
            'residual_distance': 0.0,
            'status': 'UNREACHABLE'
        }

    # ----------------------------------------------------------------------
    # 3) OPC Placement
    # ----------------------------------------------------------------------
    # per the spec:
    #   Case1: no reg => if total_sub_distance <= threshold AND sub_array has >=3 nodes => 1 OPC
    #   Case2: with reg => break into sub-sections & place 1 OPC if that section has >=3 nodes
    # skip sub-array index=0 and index=(sub_n-1) for actual placement
    import math

    # build partial sums for the sub-array
    sub_partial_sums = [0.0]*sub_n
    acc = 0.0
    for i in range(1, sub_n):
        acc += sub_distances[i-1]
        sub_partial_sums[i] = acc

    def sub_section_distance(si, ei):
        return abs(sub_partial_sums[ei] - sub_partial_sums[si])

    def place_one_opc_in_subsection(si, ei):
        # # of nodes in this sub-section = ei - si + 1
        count_sub = (ei - si + 1)
        if count_sub < 3:
            return None
        sec_dist = sub_section_distance(si, ei)
        if sec_dist <= 0:
            return None
        midpoint = sub_partial_sums[si] + sec_dist/2.0
        best_idx = None
        best_diff=1e15
        for idx in range(si+1, ei):
            if not is_valid_sub_index(idx):
                continue
            dist_here = sub_partial_sums[idx]
            diff = abs(dist_here - midpoint)
            if diff < best_diff:
                best_diff = diff
                best_idx = idx
        if best_idx is not None:
            return sub_nodes[best_idx]
        return None

    opcs = []
    if len(regens) == 0:
        # case1: no reg
        if total_sub_distance <= REGENERATOR_THRESHOLD:
            # if sub_n >= 3 => place 1 OPC
            if sub_n >= 3:
                candidate = place_one_opc_in_subsection(0, sub_n-1)
                if candidate is not None:
                    opcs.append(candidate)
    else:
        # case2: with reg => sub-sections
        # anchor indices in sub-array => 0, regIndices, sub_n-1
        anchor_idxs = [0]
        reg_map = []
        for idx, nd in enumerate(sub_nodes):
            if nd in regens:
                reg_map.append(idx)
        reg_map.sort()
        anchor_idxs.extend(reg_map)
        if (sub_n-1) not in anchor_idxs:
            anchor_idxs.append(sub_n-1)

        for i_a in range(len(anchor_idxs)-1):
            s_i = anchor_idxs[i_a]
            e_i = anchor_idxs[i_a+1]
            c_opc = place_one_opc_in_subsection(s_i, e_i)
            if c_opc:
                opcs.append(c_opc)

    # ----------------------------------------------------------------------
    # 4) Residual Distance
    # ----------------------------------------------------------------------
    # scenario1: no OPC => entire sub-array dist if no reg, else from last reg->end
    # scenario2: >=1 OPC => sum of |left-right| for each OPC + leftover from last reg->end
    def sum_sub_dist(a_i, b_i):
        # sum of distances from sub_array index=a_i..(b_i-1)
        # simpler to do partial sums:
        return abs(sub_partial_sums[b_i] - sub_partial_sums[a_i])

    if len(opcs) == 0:
        # scenario1 => no OPC
        if len(regens) == 0:
            # entire sub-array
            residual = total_sub_distance
        else:
            last_r = regens[-1]
            # find sub_array index
            lr_idx = sub_nodes.index(last_r)
            leftover = sum_sub_dist(lr_idx, sub_n-1)
            residual = leftover
    else:
        # scenario2 => sum(|L-R|) + leftover from last reg->end
        # 1) sum of |L-R|
        anchor_idxs = [0]
        reg_map = []
        for idx, nd in enumerate(sub_nodes):
            if nd in regens:
                reg_map.append(idx)
        reg_map.sort()
        anchor_idxs.extend(reg_map)
        if (sub_n-1) not in anchor_idxs:
            anchor_idxs.append(sub_n-1)

        opc_set = set(opcs)
        sum_abs_diff = 0.0
        for i_a in range(len(anchor_idxs)-1):
            s_i = anchor_idxs[i_a]
            e_i = anchor_idxs[i_a+1]
            # find if there's an OPC in (s_i+1..e_i-1)
            the_opc_idx = None
            for x in range(s_i+1, e_i):
                if sub_nodes[x] in opc_set:
                    the_opc_idx = x
                    break
            if the_opc_idx is not None:
                leftd  = abs(sub_partial_sums[the_opc_idx] - sub_partial_sums[s_i])
                rightd = abs(sub_partial_sums[e_i] - sub_partial_sums[the_opc_idx])
                sum_abs_diff += abs(leftd - rightd)

        # 2) leftover from last reg->(sub_n-1)
        leftover = 0.0
        if len(regens) > 0:
            last_r = regens[-1]
            lr_idx = sub_nodes.index(last_r)
            leftover = sum_sub_dist(lr_idx, sub_n-1)
        else:
            # if OPC but no reg => e.g. entire path is sub-array, leftover=maybe sub-array is short
            # your spec's example focuses on last reg leftover, so fallback=0
            leftover = 0.0

        residual = sum_abs_diff + leftover

    return {
        'source': source,
        'destination': destination,
        'total_distance': round(total_sub_distance,2),
        'regenerators': regens,
        'opcs': opcs,
        'residual_distance': round(residual,2),
        'status': 'OK'
    }

def analyze_all_paths(path_records):
    results = []
    for p in path_records:
        results.append(analyze_path(p))
    return results