from sklearn.metrics import roc_auc_score
import torch
from torch_geometric.utils import negative_sampling

def evaluate(model, graph, x, edge_index, edge_type, val_edges):
    model.eval()
    with torch.no_grad():
        out = model(x, edge_index, edge_type)
        pos = val_edges.T
        neg = negative_sampling(edge_index, num_nodes=graph.num_nodes, num_neg_samples=pos.size(1))

        pos_score = (out[pos[0]] * out[pos[1]]).sum(dim=1)
        neg_score = (out[neg[0]] * out[neg[1]]).sum(dim=1)

        y_true = torch.cat([torch.ones(pos_score.size(0)), torch.zeros(neg_score.size(0))])
        y_score = torch.cat([pos_score, neg_score])
        return roc_auc_score(y_true.cpu(), y_score.cpu())
