from flask import request, jsonify, render_template, session, redirect, url_for
from src.utils.model import model, graph, rel_type_to_id, entity_mappings
from src.utils.model import model, graph, flat_edge_index, flat_edge_type, rel_type_to_id, entity_mappings
from src.utils.id_resolver import resolve_pubchem_cid, resolve_umls_cui
import torch
import os
import csv
from datetime import datetime

# Optional DrugBank Integration
try:
    from src.utils.drugbank_lookup import lookup_drug_by_cid
    DRUGBANK_ENABLED = True
except ImportError:
    DRUGBANK_ENABLED = False
    lookup_drug_by_cid = lambda cid: None
try:
    from utils.drugbank_full_lookup import lookup_full_drug_info
    DRUGBANK_RICH_ENABLED = True
except ImportError:
    DRUGBANK_RICH_ENABLED = False
    lookup_full_drug_info = lambda cid: None


def register_predict(app):
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

            # Validate node ID range
            max_src = graph[src_type].num_nodes
            max_dst = graph[dst_type].num_nodes

            if not (0 <= drug1_id < max_src):
                error_msg = f"drug1_id out of range for type '{src_type}'. Max: {max_src - 1}"
                return jsonify({"error": error_msg}) if request.is_json else render_template("index.html", error=error_msg)

            if not (0 <= drug2_id < max_dst):
                error_msg = f"drug2_id out of range for type '{dst_type}'. Max: {max_dst - 1}"
                return jsonify({"error": error_msg}) if request.is_json else render_template("index.html", error=error_msg)

            rel_id = rel_type_to_id[matched_rel]

            # Run model
            with torch.no_grad():
                out = model(graph.x_dict, flat_edge_index, flat_edge_type)
                emb1 = out[:graph[src_type].num_nodes][drug1_id]
                emb2 = out[:graph[dst_type].num_nodes][drug2_id]
                score = torch.sigmoid((emb1 * emb2).sum()).item()

            # Resolve human-readable names
            raw_name1 = entity_mappings.get(src_type, {}).get(drug1_id, f"{src_type}:{drug1_id}")
            raw_name2 = entity_mappings.get(dst_type, {}).get(drug2_id, f"{dst_type}:{drug2_id}")

            drug1_name = resolve_pubchem_cid(raw_name1) if raw_name1.startswith("CID") else (
                resolve_umls_cui(raw_name1) if raw_name1.startswith("C") else raw_name1
            )
            drug2_name = resolve_pubchem_cid(raw_name2) if raw_name2.startswith("CID") else (
                resolve_umls_cui(raw_name2) if raw_name2.startswith("C") else raw_name2
            )

            # Log to CSV
            log_path = "predictions_log.csv"
            log_fields = ['timestamp', 'drug1_id', 'drug2_id', 'relation_type', 'score']
            log_data = [datetime.now().isoformat(), drug1_id, drug2_id, relation_str, score]

            file_exists = os.path.isfile(log_path)
            with open(log_path, mode='a', newline='') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(log_fields)
                writer.writerow(log_data)

            # Final response
            response = {
                "drug1_id": drug1_id,
                "drug2_id": drug2_id,
                "drug1_name": drug1_name,
                "drug2_name": drug2_name,
                "relation_type": relation_str,
                "predicted_interaction_probability": score
            }
            # Optional DrugBank info
            cid1 = raw_name1.replace("CID:", "").lstrip("0") if raw_name1.startswith("CID") else None
            cid2 = raw_name2.replace("CID:", "").lstrip("0") if raw_name2.startswith("CID") else None
            
            drug1_info = lookup_drug_by_cid(cid1) if cid1 else None
            drug2_info = lookup_drug_by_cid(cid2) if cid2 else None

            response["drug1_info"] = drug1_info
            response["drug2_info"] = drug2_info
            rich_drug1_info = lookup_full_drug_info(cid1) if cid1 else None
            rich_drug2_info = lookup_full_drug_info(cid2) if cid2 else None

            response["drug1_full_info"] = rich_drug1_info
            response["drug2_full_info"] = rich_drug2_info

            if request.is_json:
                return jsonify(response)
            else:
                session["prediction_result"] = {
                    "prediction": score,
                    "relation": relation_str,
                    "drug1_id": drug1_id,
                    "drug2_id": drug2_id,
                    "drug1_name": drug1_name,
                    "drug2_name": drug2_name
                }

                return redirect(url_for("index"))


        except Exception as e:
            return jsonify({"error": str(e)}) if request.is_json else render_template("index.html", error=str(e))
