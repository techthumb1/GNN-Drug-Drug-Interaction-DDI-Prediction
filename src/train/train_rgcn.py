import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import torch
from ogb.linkproppred import LinkPropPredDataset
from torch_geometric.data import HeteroData
from torch_geometric.transforms import ToUndirected
from src.models.rgcn_model import RGCN

def convert_to_heterodata(graph_dict):
    hetero = HeteroData()

    for (src, rel, dst), edge_index in graph_dict['edge_index_dict'].items():
        if not isinstance(edge_index, torch.Tensor):
            edge_index = torch.tensor(edge_index, dtype=torch.long)
        hetero[(src, rel, dst)].edge_index = edge_index

    for node_type, num_nodes in graph_dict['num_nodes_dict'].items():
        hetero[node_type].num_nodes = num_nodes

    return hetero

def train():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Load and convert dataset
    dataset = LinkPropPredDataset(name='ogbl-biokg')
    graph_dict = dataset[0]
    data = convert_to_heterodata(graph_dict)
    data = ToUndirected()(data)
    data = data.to(device)

    metadata = (list(data.node_types), list(data.edge_types))
    num_nodes_dict = {node_type: data[node_type].num_nodes for node_type in data.node_types}

    model = RGCN(
        metadata=metadata,
        num_nodes_dict=num_nodes_dict,
        hidden_channels=64,
        out_channels=2,
        num_layers=2
    ).to(device)

    # x_dict with input indices
    x_dict = {k: torch.arange(v, device=device) for k, v in num_nodes_dict.items()}

    # Combine edge_index and edge_type
    all_edge_index = []
    all_edge_type = []

    for i, (edge_type, edge_index) in enumerate(data.edge_index_dict.items()):
        all_edge_index.append(edge_index)
        all_edge_type.append(torch.full((edge_index.shape[1],), i, dtype=torch.long))

    edge_index = torch.cat(all_edge_index, dim=1).to(device)
    edge_type = torch.cat(all_edge_type, dim=0).to(device)

    out = model(x_dict, edge_index, edge_type)

    # After training completes
    torch.save({
        "model_state_dict": model.state_dict()
    }, "models/model_checkpoint.pt")


    print("Forward pass successful! Output shapes:")
    print("Output shape:", out.shape)


if __name__ == "__main__":
    train()
