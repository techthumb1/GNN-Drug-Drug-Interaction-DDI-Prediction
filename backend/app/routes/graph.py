from flask import request, jsonify, render_template
from src.utils.model import model, graph, flat_edge_type, entity_mappings
from src.explain.explain_pg import run_pgexplainer

def register_graph_routes(app):

    @app.route("/graph_data")
    def graph_data():
        drug1_id = request.args.get("drug1_id", "25")
        drug2_id = request.args.get("drug2_id", "88")

        try:
            drug1_id = int(drug1_id)
            drug2_id = int(drug2_id)
        except ValueError:
            return jsonify({"error": "Invalid drug1_id or drug2_id"}), 400

        result = run_pgexplainer(model, graph, drug1_id, drug2_id)
        edges = result["important_edges"]
        weights = result["edge_mask_scores"]

        # Node & link construction
        nodes = {drug1_id, drug2_id}
        links = []

        for (src, tgt), weight in zip(zip(*edges), weights):
            nodes.update([src, tgt])
            links.append({
                "source": str(src),
                "target": str(tgt),
                "weight": round(weight, 4)
            })

        # Build labeled node list
        node_list = []
        for node_id in nodes:
            node_type = "unknown"
            label = f"Node {node_id}"
        
            for entity_type, mapping in entity_mappings.items():
                if node_id in mapping:
                    label = mapping[node_id]
                    node_type = entity_type  # drug, protein, disease, etc.
                    break
                
            node_list.append({
                "id": str(node_id),
                "label": label,
                "type": node_type
            })
        
        return jsonify({
            "nodes": node_list,
            "links": links
        })

    @app.route("/graph")
    def graph_page():
        return render_template("graph.html")
