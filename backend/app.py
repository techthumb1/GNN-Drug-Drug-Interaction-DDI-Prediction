import sys
import os
import torch
from flask import Flask, request, jsonify

# Ensure src is in Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.rgcn_model import RGCN
from src.data.load_biokg import load_biokg_as_hetero

app = Flask(__name__)

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load graph
graph = load_biokg_as_hetero()
graph = graph.to(device)

from torch_geometric.data import HeteroData

# Manually reconstruct edge_type
edge_index_dict = graph.edge_index_dict
rel_type_to_id = {rel: i for i, rel in enumerate(graph.edge_types)}
edge_types = []
edge_indices = []

for (src, rel, dst), edge_index in edge_index_dict.items():
    edge_types.append(torch.full((edge_index.size(1),), rel_type_to_id[(src, rel, dst)]))
    edge_indices.append(edge_index)

# Concatenate into flat tensors
flat_edge_index = torch.cat(edge_indices, dim=1)
flat_edge_type = torch.cat(edge_types, dim=0)

# Prepare model inputs
metadata = graph.metadata()
num_nodes_dict = {k: v.num_nodes for k, v in graph.node_items()}

# Load checkpoint
checkpoint = torch.load("model_checkpoint.pt", map_location=device)

# Initialize model
model = RGCN(
    metadata=metadata,
    num_nodes_dict=num_nodes_dict,
    hidden_channels=64,
    out_channels=2,
    num_layers=2
).to(device)

# Load weights and set to eval mode
model.load_state_dict(checkpoint["model_state_dict"])
model.eval()

@app.route("/")
def home():
    return "✅ DDI Prediction API is running."

@app.route("/predict", methods=["POST"])
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        drug1_id = int(data["drug1_id"])
        drug2_id = int(data["drug2_id"])
        relation_type = "drug-drug_cancer"  # You can parameterize this later

        with torch.no_grad():
            out = model(graph.x_dict, flat_edge_index, flat_edge_type)
            
            print("Model output shape:", out.shape)
            
            max_id = out.shape[0] - 1
            print("Requested drug1_id:", drug1_id, "drug2_id:", drug2_id)
            
            if drug1_id > max_id or drug2_id > max_id:
                return jsonify({"error": f"Drug ID out of range. Max is {max_id}"}), 400
            
            emb1 = out[drug1_id]
            emb2 = out[drug2_id]
            score = torch.sigmoid((emb1 * emb2).sum()).item()

        return jsonify({
            "drug1_id": drug1_id,
            "drug2_id": drug2_id,
            "relation_type": relation_type,
            "predicted_interaction_probability": score
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
