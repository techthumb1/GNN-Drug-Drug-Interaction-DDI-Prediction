import sys
import os
import torch
import csv
from datetime import datetime
from flask import Flask, request, jsonify, render_template

# Ensure src is in Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.rgcn_model import RGCN
from src.data.load_biokg import load_biokg_as_hetero

app = Flask(__name__)

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load graph
graph = load_biokg_as_hetero().to(device)

# Manually reconstruct edge_type
edge_index_dict = graph.edge_index_dict
rel_type_to_id = {rel: i for i, rel in enumerate(graph.edge_types)}
print("Available relation types:", rel_type_to_id.keys())
edge_types, edge_indices = [], []

for (src, rel, dst), edge_index in edge_index_dict.items():
    edge_types.append(torch.full((edge_index.size(1),), rel_type_to_id[(src, rel, dst)]))
    edge_indices.append(edge_index)

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

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/relations", methods=["GET"])
def get_relation_types():
    return jsonify(sorted(set(k[1] for k in rel_type_to_id)))

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json() if request.is_json else request.form

        drug1_id = int(data["drug1_id"])
        drug2_id = int(data["drug2_id"])
        relation_str = data.get("relation_type", "drug-drug_cancer")

        # Find matching relation tuple
        matched_rel = next((k for k in rel_type_to_id if k[1] == relation_str), None)

        if matched_rel is None:
            return jsonify({"error": f"Invalid relation type: {relation_str}"}), 400

        rel_id = rel_type_to_id[matched_rel]

        with torch.no_grad():
            out = model(graph.x_dict, flat_edge_index, flat_edge_type)

            drug_embeddings = out[:graph['drug'].num_nodes]
            max_id = drug_embeddings.shape[0] - 1

            if drug1_id > max_id or drug2_id > max_id:
                return jsonify({"error": f"Drug ID out of range. Max allowed is {max_id}"}), 400

            emb1 = drug_embeddings[drug1_id]
            emb2 = drug_embeddings[drug2_id]
            score = torch.sigmoid((emb1 * emb2).sum()).item()

        log_path = "predictions_log.csv"
        log_fields = ['timestamp', 'drug1_id', 'drug2_id', 'relation_type', 'score']
        log_data = [datetime.now().isoformat(), drug1_id, drug2_id, relation_str, score]

        file_exists = os.path.isfile(log_path)
        with open(log_path, mode='a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(log_fields)
            writer.writerow(log_data)

        response = {
            "drug1_id": drug1_id,
            "drug2_id": drug2_id,
            "relation_type": relation_str,
            "predicted_interaction_probability": score
        }

        return jsonify(response) if request.is_json else f"<h2>Prediction ({relation_str}): {score:.4f}</h2>"

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)