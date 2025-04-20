'''
NOTE: This is a manual implementation of `to_homogeneous()` from PyG 2.6.1
      It’s used because some builds (especially from data.pyg.org) don’t expose the function properly.
      Replace with `from torch_geometric.utils import to_homogeneous` once a verified build is in use.

'''

import torch
from torch_geometric.data import HeteroData
from torch_geometric.data import Data

def to_homogeneous(data: HeteroData) -> Data:
    # Combine all node features
    node_types = list(data.node_types)
    node_offset = 0
    x_all = []
    node_slices = {}
    for node_type in node_types:
        x = data[node_type].x if 'x' in data[node_type] else torch.zeros((data[node_type].num_nodes, 0))
        x_all.append(x)
        node_slices[node_type] = (node_offset, node_offset + data[node_type].num_nodes)
        node_offset += data[node_type].num_nodes
    x = torch.cat(x_all, dim=0)

    edge_index_all = []
    for rel in data.edge_types:
        src, _, dst = rel
        edge_index = data[rel].edge_index
        edge_index = edge_index.clone()
        edge_index[0] += node_slices[src][0]
        edge_index[1] += node_slices[dst][0]
        edge_index_all.append(edge_index)
    edge_index = torch.cat(edge_index_all, dim=1)

    return Data(x=x, edge_index=edge_index)
