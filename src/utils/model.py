import torch
from src.models.rgcn_model import RGCN
from src.data.load_biokg import load_biokg_as_hetero
from src.utils.mapping_loader import load_entity_mappings

# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load graph
graph = load_biokg_as_hetero().to(device)
metadata = graph.metadata()
num_nodes_dict = {k: v.num_nodes for k, v in graph.node_items()}
rel_type_to_id = {rel: i for i, rel in enumerate(graph.edge_types)}

# Edge construction
edge_types, edge_indices = [], []
for (src, rel, dst), edge_index in graph.edge_index_dict.items():
    edge_types.append(torch.full((edge_index.size(1),), rel_type_to_id[(src, rel, dst)]))
    edge_indices.append(edge_index)

flat_edge_index = torch.cat(edge_indices, dim=1)
flat_edge_type = torch.cat(edge_types, dim=0)

# Load model
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

# Load entity name mapping
entity_mappings = load_entity_mappings("dataset/ogbl_biokg/mapping")

print(f"✅ flat_edge_index shape: {flat_edge_index.shape}")
print(f"✅ flat_edge_type shape: {flat_edge_type.shape}")
