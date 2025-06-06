import os
import shutil
import torch
from ogb.linkproppred import LinkPropPredDataset
from torch_geometric.transforms import ToUndirected
from torch_geometric.data import HeteroData

# Fix: Avoid recursive torch.load override
original_torch_load = torch.load
torch.load = lambda *args, **kwargs: original_torch_load(*args, **{**kwargs, "weights_only": False})


def load_biokg_as_hetero():
    dataset_root = "dataset/biokg"

    # CLEANUP STEP: Remove partially extracted dataset if exists
    if os.path.exists(os.path.join(dataset_root, "raw")):
        print("[WARN] Removing existing dataset directory to prevent OGB crash...")
        shutil.rmtree(dataset_root)

    # Download and extract dataset cleanly
    dataset = LinkPropPredDataset(name="ogbl-biokg", root=dataset_root)
    data = dataset[0]

    hetero_data = HeteroData()
    edge_index_dict = data['edge_index_dict']
    num_nodes_dict = data['num_nodes_dict']

    # Add node types with dummy features
    for node_type, count in num_nodes_dict.items():
        hetero_data[node_type].x = torch.arange(count)

    # Add edges per relation
    for (src, rel, dst), edge_index in edge_index_dict.items():
        hetero_data[(src, rel, dst)].edge_index = torch.tensor(edge_index, dtype=torch.long)

    # Optionally make graph undirected
    hetero_data = ToUndirected()(hetero_data)

    return hetero_data
