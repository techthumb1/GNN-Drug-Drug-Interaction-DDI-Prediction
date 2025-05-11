import torch
import torch.nn.functional as F
from src.utils.sage_loader import load_sage_and_homograph

def run_explainer(model, graph, drug1_id, drug2_id, top_k=5):
    with torch.no_grad():
        embeddings = model(graph.x, graph.edge_index)

    drug1_vec = embeddings[drug1_id]
    drug2_vec = embeddings[drug2_id]

    drug1_sim = F.cosine_similarity(drug1_vec.unsqueeze(0), embeddings, dim=1)
    drug2_sim = F.cosine_similarity(drug2_vec.unsqueeze(0), embeddings, dim=1)

    top_drug1 = torch.topk(drug1_sim, top_k + 1)
    top_drug2 = torch.topk(drug2_sim, top_k + 1)

    # Remove self-match (if any) and pair with scores
    drug1_neighbors = [
        (idx.item(), round(score.item(), 4))
        for idx, score in zip(top_drug1.indices, top_drug1.values)
        if idx.item() != drug1_id
    ][:top_k]

    drug2_neighbors = [
        (idx.item(), round(score.item(), 4))
        for idx, score in zip(top_drug2.indices, top_drug2.values)
        if idx.item() != drug2_id
    ][:top_k]

    interaction_score = torch.sigmoid((drug1_vec * drug2_vec).sum()).item()

    return {
        "prediction_score": round(interaction_score, 4),
        "top_neighbors_drug1": drug1_neighbors,
        "top_neighbors_drug2": drug2_neighbors
    }

if __name__ == "__main__":
    model, graph = load_sage_and_homograph()
    result = run_explainer(model, graph, drug1_id=25, drug2_id=88)
    print(result)
