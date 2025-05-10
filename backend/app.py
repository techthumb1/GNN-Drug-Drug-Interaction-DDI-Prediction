import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sys
import os
import torch
import csv
from dotenv import load_dotenv
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask import send_file
import pandas as pd
import io
from src.utils.mapping_loader import load_entity_mappings
from flask import redirect, url_for, session
from src.models.rgcn_model import RGCN
from src.data.load_biokg import load_biokg_as_hetero
from src.explain.explain_ddi import run_explainer
from src.utils.id_resolver import resolve_pubchem_cid, resolve_umls_cui



load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
mapping_dir = os.path.join(BASE_DIR, 'dataset', 'ogbl_biokg', 'mapping')

entity_mappings = load_entity_mappings(mapping_dir)

# Ensure src is in Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback_key")

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load graph
graph = load_biokg_as_hetero().to(device)

# Manually reconstruct edge_type
edge_index_dict = graph.edge_index_dict
rel_type_to_id = {rel: i for i, rel in enumerate(graph.edge_types)}
#print("Available relation types:", rel_type_to_id.keys())
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
checkpoint = torch.load("checkpoints/model_checkpoint.pt", map_location=device)

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
    result = session.pop("prediction_result", None)
    return render_template("index.html", **(result or {}))

@app.route("/relations", methods=["GET"])
def get_relation_types():
    return jsonify(sorted(set(k[1] for k in rel_type_to_id)))

from src.explain.explain_ddi import run_explainer

@app.route("/explain", methods=["GET"])
def explain():
    try:
        drug1_id = int(request.args.get("drug1_id"))
        drug2_id = int(request.args.get("drug2_id"))
        relation = request.args.get("relation_type")

        matched_rel = next((k for k in rel_type_to_id if k[1] == relation), None)
        if matched_rel is None:
            return jsonify({"error": f"Invalid relation type: {relation}"}), 400

        explanation = run_explainer(model, graph, drug1_id, drug2_id, matched_rel)
        return jsonify(explanation)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json() if request.is_json else request.form

        relation_str = data.get("relation_type", "drug-drug_cancer")
        matched_rel = next((k for k in rel_type_to_id if k[1] == relation_str), None)

        if matched_rel is None:
            error_msg = f"Invalid relation type: {relation_str}"
            return jsonify({"error": error_msg}) if request.is_json else render_template("index.html", error=error_msg)

        src_type, _, dst_type = matched_rel
        drug1_id = int(data["drug1_id"])
        drug2_id = int(data["drug2_id"])

        max_src = graph[src_type].num_nodes
        max_dst = graph[dst_type].num_nodes

        if drug1_id >= max_src or drug1_id < 0:
            error_msg = f"drug1_id out of range for type '{src_type}'. Must be 0 to {max_src - 1}."
            return jsonify({"error": error_msg}) if request.is_json else render_template("index.html", error=error_msg)

        if drug2_id >= max_dst or drug2_id < 0:
            error_msg = f"drug2_id out of range for type '{dst_type}'. Must be 0 to {max_dst - 1}."
            return jsonify({"error": error_msg}) if request.is_json else render_template("index.html", error=error_msg)

        rel_id = rel_type_to_id[matched_rel]

        with torch.no_grad():
            out = model(graph.x_dict, flat_edge_index, flat_edge_type)
            emb1 = out[:graph[src_type].num_nodes][drug1_id]
            emb2 = out[:graph[dst_type].num_nodes][drug2_id]
            score = torch.sigmoid((emb1 * emb2).sum()).item()
            # Look up entity names for display
            raw_name1 = entity_mappings.get(src_type, {}).get(drug1_id, f"{src_type}:{drug1_id}")
            raw_name2 = entity_mappings.get(dst_type, {}).get(drug2_id, f"{dst_type}:{drug2_id}")

            if raw_name1.startswith("CID"):
                drug1_name = resolve_pubchem_cid(raw_name1)
            elif raw_name1.startswith("C"):
                drug1_name = resolve_umls_cui(raw_name1)
            else:
                drug1_name = raw_name1

            if raw_name2.startswith("CID"):
                drug2_name = resolve_pubchem_cid(raw_name2)
            elif raw_name2.startswith("C"):
                drug2_name = resolve_umls_cui(raw_name2)
            else:
                drug2_name = raw_name2

        # Log
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
            "drug1_name": drug1_name,
            "drug2_name": drug2_name,
            "relation_type": relation_str,
            "predicted_interaction_probability": score
        }

        if request.is_json:
            return jsonify(response)
        else:
            session["prediction_result"] = {
                "prediction": score,
                "relation": relation_str,
                "response": response,
                "drug1_id": drug1_id,
                "drug2_id": drug2_id
            }

            return redirect(url_for("index"))
    except Exception as e:
        return jsonify({"error": str(e)}) if request.is_json else render_template("index.html", error=str(e))

@app.route("/batch", methods=["GET", "POST"])
def batch():
    if request.method == "POST":
        file = request.files["file"]
        if not file or not file.filename.endswith(".csv"):
            return render_template("batch.html", error="Please upload a valid CSV file.")

        df = pd.read_csv(file)
        results = []

        for _, row in df.iterrows():
            try:
                d1, d2 = int(row["drug1_id"]), int(row["drug2_id"])
                relation = row["relation_type"]

                matched_rel = next((k for k in rel_type_to_id if k[1] == relation), None)
                if not matched_rel:
                    score = "Invalid Relation"
                else:
                    src_type, _, dst_type = matched_rel
                    out = model(graph.x_dict, flat_edge_index, flat_edge_type)
                    emb1 = out[:graph[src_type].num_nodes][d1]
                    emb2 = out[:graph[dst_type].num_nodes][d2]
                    score = torch.sigmoid((emb1 * emb2).sum()).item()

                results.append({
                    "drug1_id": d1,
                    "drug2_id": d2,
                    "relation_type": relation,
                    "predicted_score": score
                })
            except Exception as e:
                results.append({
                    "drug1_id": row.get("drug1_id", ""),
                    "drug2_id": row.get("drug2_id", ""),
                    "relation_type": row.get("relation_type", ""),
                    "predicted_score": str(e)
                })

        output_df = pd.DataFrame(results)
        output_stream = io.StringIO()
        output_df.to_csv(output_stream, index=False)
        output_stream.seek(0)

        return send_file(io.BytesIO(output_stream.read().encode()), mimetype='text/csv',
                         download_name="predictions.csv", as_attachment=True)

    return render_template("batch.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)