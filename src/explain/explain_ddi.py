import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import torch
from torch_geometric.explain import GNNExplainer
import torch_geometric
from src.models.rgcn_model import RGCN
from src.data.load_biokg import load_biokg_as_hetero

# Load model and graph
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
graph = load_biokg_as_hetero().to(device)
metadata = graph.metadata()
num_nodes_dict = {k: v.num_nodes for k, v in graph.node_items()}

model = RGCN(
    metadata=metadata,
    num_nodes_dict=num_nodes_dict,
    hidden_channels=64,
    out_channels=2,
    num_layers=2
).to(device)

checkpoint = torch.load("model_checkpoint.pt", map_location=device)
model.load_state_dict(checkpoint["model_state_dict"])
model.eval()

# Select a specific prediction to explain
target_drug1 = 101
target_drug2 = 202

# Flatten edge indices and edge types
flat_edge_index, flat_edge_type = torch_geometric.utils.to_undirected(
    graph.edge_index_dict, graph.edge_type_dict
)

# Run forward pass
out = model(graph.x_dict, flat_edge_index, flat_edge_type)
pred = torch.sigmoid((out[target_drug1] * out[target_drug2]).sum()).item()
print(f"Prediction: {pred:.4f}")

# Use GNNExplainer
explainer = GNNExplainer(model, epochs=100, return_type='log_prob')

# NOTE: We treat the drug as the center node
explanation = explainer.explain_node(
    node_idx=target_drug1,
    x=graph.x_dict,
    edge_index=flat_edge_index,
    edge_type=flat_edge_type
)

print("Important edges:", explanation.edge_mask)
