import json
from flask import Blueprint, request, jsonify, Response
from services.reconstruction_service import ReconstructionService

export_bp = Blueprint("export", __name__)


@export_bp.route("/api/export/html", methods=["POST"])
def export_html():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "No design data provided."}), 400

    title = data.get("title", "PIXEL2EDIT Exported Design")
    design = data.get("design", data)

    html_content = ReconstructionService.generate_standalone_html(design, title=title)

    return Response(
        html_content,
        mimetype="text/html",
        headers={"Content-Disposition": "attachment; filename=design_pixel2edit.html"}
    )


@export_bp.route("/api/export/json", methods=["POST"])
def export_json():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "No design data provided."}), 400

    design = data.get("design", data)
    json_str = json.dumps(design, indent=2)

    return Response(
        json_str,
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=design_pixel2edit.json"}
    )
