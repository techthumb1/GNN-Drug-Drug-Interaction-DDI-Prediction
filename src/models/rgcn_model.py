import torch
from torch.nn import ModuleDict, Embedding
from torch_geometric.nn import RGCNConv

class RGCN(torch.nn.Module):
    def __init__(self, metadata, num_nodes_dict, hidden_channels=64, out_channels=2, num_layers=2):
        super().__init__()
        self.embeddings = ModuleDict()

        for node_type in metadata[0]:  # node types
            self.embeddings[node_type] = Embedding(
                num_embeddings=num_nodes_dict[node_type],
                embedding_dim=hidden_channels
            )

        self.convs = torch.nn.ModuleList()
        for i in range(num_layers):
            self.convs.append(RGCNConv(
                in_channels=hidden_channels,
                out_channels=hidden_channels if i < num_layers - 1 else out_channels,
                num_relations=len(metadata[1]),  # edge types
                num_bases=30
            ))

    def forward(self, x_dict, edge_index, edge_type):
        x = torch.cat([self.embeddings[key](x_dict[key]) for key in x_dict], dim=0)
        for conv in self.convs:
            x = conv(x, edge_index, edge_type)
        return x[:, 1]
