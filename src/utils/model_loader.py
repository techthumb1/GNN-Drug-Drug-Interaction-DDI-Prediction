# src/utils/model_loader.py
import torch
from torch_geometric.data import HeteroData
from src.data.load_biokg import load_biokg_as_hetero
from src.models.rgcn_model import RGCN
from src.models.graphsage_model import GraphSAGE

def load_model_and_graph(checkpoint_path="models/model_checkpoint.pt", device=None):
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    graph = load_biokg_as_hetero()
    metadata = graph.metadata()
    num_nodes_dict = {k: v.num_nodes for k, v in graph.node_items()}

    model = RGCN(
        metadata=metadata,
        num_nodes_dict=num_nodes_dict,
        hidden_channels=64,
        out_channels=2,
        num_layers=2
    ).to(device)

    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"], strict=False)
    model.eval()

    # Use built-in method, no need to import ToHomogeneous
    homo_graph = graph.to_homogeneous().to(device)

    return model, homo_graph


def load_graphsage_model(homo_graph, in_channels):
    model = GraphSAGE(in_channels=in_channels)
    return model
