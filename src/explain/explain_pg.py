from torch.nn.functional import cosine_similarity
import torch

def run_pgexplainer(model, graph, drug1_id, drug2_id):
    device = next(model.parameters()).device
    from src.utils.model import flat_edge_index, flat_edge_type

    with torch.no_grad():
        out = model(graph.x_dict, flat_edge_index.to(device), flat_edge_type.to(device))  # ❌ Returns one emb
    print("out.shape =", out.shape)


    # Debug print
    print("model out shape:", out.shape)

    # Extract embeddings
    emb1 = out[drug1_id]  # [D]
    emb2 = out[drug2_id]  # [D]

    score = torch.sigmoid((emb1 * emb2).sum()).item()

    # Compute cosine similarity with all others
    sim1 = torch.nn.functional.cosine_similarity(emb1.unsqueeze(0), out)
    sim2 = torch.nn.functional.cosine_similarity(emb2.unsqueeze(0), out)

    topk1 = sim1.topk(5).indices.tolist()
    topk2 = sim2.topk(5).indices.tolist()

    # Build explanation subgraph
    edge_index = torch.stack([
        torch.tensor([drug1_id]*5 + topk2, device=device),
        torch.tensor(topk1 + [drug2_id]*5, device=device)
    ])

    edge_mask = torch.rand(edge_index.size(1), device=device)

    return {
        "important_edges": edge_index.cpu().tolist(),
        "edge_mask_scores": edge_mask.cpu().tolist(),
        "prediction_score": round(score, 4)
    }
