#!/usr/bin/env python3
"""
input_parser.py

Parses each line of the Simon output file. The format is:
   SRC->DST (Cost: X) n0 (dist0) n1 (dist1) n2 (dist2) ... nK (distK) FINAL_NODE (LinkCount: Y)

Where each "nI (distI)" means:
    "nI" is a node ID
    "(distI)" is the distance from nI to the *next* node in the path.
After the last pair "nK (distK)", the line has a trailing node (FINAL_NODE)
which is the ultimate destination, with no parentheses since there's no next node.

Example:
  1->24 (Cost: 6320.02) 1 (0.01) 25 (1040.00) 30 (1200.00) ... 48 (0.01) 24 (LinkCount: 8)

We produce a list of path_records, each a dict:
{
  'source': int,
  'destination': int,
  'total_cost': float,
  'nodes': [ (nodeID, distanceToNext), (nodeID, distanceToNext), ..., (finalNode, 0.0) ],
  'unparsed_line': str
}
"""

import re

def parse_simon_output_file(filepath):
    """
    Parses the entire file into a list of path dictionaries.
    """

    # Regex for the initial "SRC->DST (Cost: XXX)" part
    line_pattern = re.compile(
        r'^(\d+)->(\d+)\s+\(Cost:\s*([\d\.]+)\)\s+(.*)$'
    )
    # Regex to match pairs of the form:  NNN (NNN.NN)
    # e.g.  25 (1040.00),  48 (0.01)
    node_pair_pattern = re.compile(r'(\d+)\s*\(\s*([\d\.]+)\s*\)')

    # We may want to remove trailing (LinkCount: X) text at the end:
    linkcount_pattern = re.compile(r'\(LinkCount:\s*\d+\)', re.IGNORECASE)

    path_records = []

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            m = line_pattern.match(line)
            if not m:
                # Could not match the basic line structure, skip
                continue

            src_str, dst_str, cost_str, remainder = m.groups()
            source = int(src_str)
            destination = int(dst_str)
            try:
                total_cost = float(cost_str)
            except ValueError:
                total_cost = 0.0

            # Remove the trailing (LinkCount: X) if present
            remainder = linkcount_pattern.sub('', remainder).strip()

            # Now parse all the "node (distance)" pairs
            pairs = node_pair_pattern.findall(remainder)
            # each element of pairs is (nodeID_str, distance_str)

            # We also need the final node (which is typically a raw integer without parentheses) at the end
            # e.g. "48 (0.01) 24"
            # After removing those pairs, the last token should be that final node
            # We'll do a quick trick: we can remove each matched substring from a local copy
            # but simpler might be to do a big split and compare.
            # We'll just re-split the remainder by whitespace and see what's left after the pairs.

            # First, build a list of nodeIDs and distances from the pairs
            node_list = []
            dist_list = []
            for (nid_str, dist_str) in pairs:
                nid = int(nid_str)
                dist_val = float(dist_str)
                node_list.append(nid)
                dist_list.append(dist_val)

            # We must figure out the leftover final node
            # One approach: re-split 'remainder' on whitespace, then remove pairs
            # Or simpler approach: the final node is typically the last integer in 'remainder' that's not in parentheses
            tokens = remainder.split()
            # We'll find the last integer not matched by node_pair_pattern

            # Because each pair is "N (D)", let's do a simpler approach: after the last pair, the next token should be the final node:
            # Example remainder: "1 (0.01) 25 (1040.00) 30 (1200.00) ... 48 (0.01) 24"
            # pairs => [("1","0.01"),("25","1040.00"), ...("48","0.01")]
            # final node => "24"

            # Let's locate the last pair string in the remainder, then see what's after it
            final_node_id = destination  # fallback if we fail logic
            if pairs:
                # last pair is pairs[-1], let's see the node ID
                last_pair_str = f"{pairs[-1][0]} ({pairs[-1][1]}"
                # that occurs in remainder, we take the substring after that
                idx = remainder.rfind(last_pair_str)
                if idx >= 0:
                    after_str = remainder[idx + len(last_pair_str):].strip()
                    # e.g. after_str might start with a closing parenthesis ) plus space, then the final node
                    after_str = after_str.lstrip(" )\t")
                    # hopefully the first token is the final node
                    # try to parse an int from that
                    leftover_tokens = after_str.split(None, 1)
                    if leftover_tokens:
                        try:
                            final_node_id = int(leftover_tokens[0])
                        except ValueError:
                            final_node_id = destination  # fallback
            else:
                # no pairs => direct link?
                # In that rare case, maybe it's "1->2 (Cost: 800.02) 1 (0.01) 2"
                # pairs => [("1","0.01")]
                # We'll handle it or fallback
                pass

            # So now we interpret the path as:
            # node_list[0] -> node_list[1] has dist_list[0]
            # node_list[1] -> node_list[2] has dist_list[1]
            # ...
            # node_list[K] -> final_node_id has dist_list[K]
            # Then the final node has distance 0
            # But watch out if we only have 0 pairs => direct link from source to destination
            full_nodes = []
            if len(node_list) == 0:
                # Possibly just the source in parentheses or something minimal
                # We'll treat this as direct link from src to dst
                # The user might have e.g. "1 (0.01) 2"
                # Hard to parse. We'll fallback
                full_nodes = [(source, 0.0), (destination, 0.0)]
            else:
                # We do node_list[0..K], plus final node
                # Distances => dist_list[0..K]
                # We'll place them as (node, distanceToNext)
                K = len(node_list)
                # e.g. if K=8, we have node_list[0..7], dist_list[0..7]
                for i in range(K):
                    nd = node_list[i]
                    dist_to_next = dist_list[i]
                    full_nodes.append((nd, dist_to_next))
                # now append the final node with distance=0
                full_nodes.append((final_node_id, 0.0))

            path_dict = {
                'source': source,
                'destination': destination,
                'total_cost': total_cost,
                'nodes': full_nodes,  # list of (nodeID, distanceToNext)
                'unparsed_line': line
            }
            path_records.append(path_dict)

    return path_records