import torch

def filter_drug_drug_edges(graph, target_edge_type_id=0):
    """
    Filter edges of a specific relation type (e.g., DDI).
    Default assumes edge type ID 0 corresponds to drug-drug interactions.
    """
    ddi_mask = (graph.edge_type == target_edge_type_id)
    ddi_edges = graph.edge_index[:, ddi_mask]
    return ddi_edges
