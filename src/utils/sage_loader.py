import torch
from torch_geometric.utils import to_homogeneous
from src.data.load_biokg import load_biokg_as_hetero
from src.models.graphsage_model import GraphSAGE

def load_sage_and_homograph(device="cpu"):
    hetero_data = load_biokg_as_hetero()
    print("✅ Loaded hetero_data:", type(hetero_data))

    # Convert to homogeneous
    graph = to_homogeneous(hetero_data)
    print("✅ After to_homogeneous:", type(graph))

    # Ensure node features exist
    if not hasattr(graph, 'x') or graph.x is None or graph.x.dim() != 2:
        num_nodes = graph.num_nodes
        graph.x = torch.randn(num_nodes, 128)
        print("✅ Injected random node features:", graph.x.shape)

    model = GraphSAGE(
        in_channels=graph.x.shape[1],
        hidden_channels=256,
        out_channels=2
    ).to(device)

    return model, graph
