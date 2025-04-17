from flask import request, render_template, send_file
import pandas as pd
import torch
import io
from src.utils.model import model, graph, flat_edge_index, flat_edge_type, rel_type_to_id

def register_batch(app):
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
                    d1 = int(row["drug1_id"])
                    d2 = int(row["drug2_id"])
                    rel = row["relation_type"]
                    matched_rel = next((k for k in rel_type_to_id if k[1] == rel), None)

                    if matched_rel is None:
                        score = "Invalid relation"
                    else:
                        src_type, _, dst_type = matched_rel
                        out = model(graph.x_dict, flat_edge_index, flat_edge_type)
                        emb1 = out[:graph[src_type].num_nodes][d1]
                        emb2 = out[:graph[dst_type].num_nodes][d2]
                        score = torch.sigmoid((emb1 * emb2).sum()).item()

                    results.append({
                        "drug1_id": d1,
                        "drug2_id": d2,
                        "relation_type": rel,
                        "predicted_score": score
                    })
                except Exception as e:
                    results.append({
                        "drug1_id": row.get("drug1_id", ""),
                        "drug2_id": row.get("drug2_id", ""),
                        "relation_type": row.get("relation_type", ""),
                        "predicted_score": str(e)
                    })

            df_out = pd.DataFrame(results)
            buffer = io.StringIO()
            df_out.to_csv(buffer, index=False)
            buffer.seek(0)

            return send_file(
                io.BytesIO(buffer.read().encode()),
                mimetype='text/csv',
                download_name='predictions.csv',
                as_attachment=True
            )

        return render_template("batch.html")
