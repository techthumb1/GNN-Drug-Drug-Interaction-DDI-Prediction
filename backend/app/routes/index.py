from flask import render_template, jsonify, request, session, send_file
from src.utils.model import model, graph, rel_type_to_id
from src.utils.id_resolver import resolve_pubchem_cid, resolve_umls_cui
import os

def register_index(app):
    @app.route("/", methods=["GET"])
    def index():
        result = session.pop("prediction_result", None)
        error = request.args.get("error")
        return render_template("index.html", prediction_result=result, error=error)

    @app.route("/relations", methods=["GET"])
    def get_relation_types():
        return jsonify(sorted(set(k[1] for k in rel_type_to_id)))

    @app.route("/download_log", methods=["GET"])
    def download_log():
        log_path = "predictions_log.csv"
        if os.path.exists(log_path):
            return send_file(log_path, as_attachment=True)
        return "No prediction log found.", 404

    return app
