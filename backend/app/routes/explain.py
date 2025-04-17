from flask import request, jsonify, render_template
from src.utils.model import model, graph, rel_type_to_id
from src.explain.explain_ddi import run_explainer

# Add the HTML formatter
def format_explanation_as_html(result, drug1_id, drug2_id):
    pred_score = result["prediction_score"]
    neighbors1 = result["top_neighbors_drug1"]
    neighbors2 = result["top_neighbors_drug2"]

    html = f"""
    <h2>Prediction Score: <span style='color: #007acc;'>{pred_score}</span></h2>
    <div style="display: flex; gap: 40px;">
        <div>
            <h3>Top Neighbors for Drug {drug1_id}</h3>
            <table border="1" cellpadding="8" cellspacing="0">
                <tr><th>Node ID</th><th>Similarity</th></tr>
                {''.join(f'<tr><td>{nid}</td><td>{score}</td></tr>' for nid, score in neighbors1)}
            </table>
        </div>
        <div>
            <h3>Top Neighbors for Drug {drug2_id}</h3>
            <table border="1" cellpadding="8" cellspacing="0">
                <tr><th>Node ID</th><th>Similarity</th></tr>
                {''.join(f'<tr><td>{nid}</td><td>{score}</td></tr>' for nid, score in neighbors2)}
            </table>
        </div>
    </div>
    """
    return html


def register_explain(app):
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

    @app.route("/explain_graph")
    def explain_graph():
        return jsonify({
            "nodes": [
                {"id": "25", "label": "Drug 1"},
                {"id": "88", "label": "Drug 2"},
                {"id": "X", "label": "Intermediate"}
            ],
            "links": [
                {"source": "25", "target": "X"},
                {"source": "X", "target": "88"}
            ]
        })

    @app.route("/explain_view")
    def explain_view():
        try:
            drug1_id = int(request.args.get("drug1_id"))
            drug2_id = int(request.args.get("drug2_id"))

            result = run_explainer(model, graph, drug1_id, drug2_id)
            html_content = format_explanation_as_html(result, drug1_id, drug2_id)

            return render_template("explanation.html", html_output=html_content)

        except Exception as e:
            return render_template("explanation.html", html_output=f"<p style='color:red;'>Error: {e}</p>")
