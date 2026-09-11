import os
from flask import Blueprint, jsonify, request
from config import Config, BASE_DIR

health_bp = Blueprint("health", __name__)


@health_bp.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "app": "PIXEL2EDIT",
        "version": "1.0.0",
        "gemini_configured": Config.is_gemini_configured(),
        "model": Config.get_gemini_model(),
        "max_upload_mb": Config.MAX_UPLOAD_MB
    })


@health_bp.route("/api/config/key", methods=["POST"])
def set_api_key():
    data = request.get_json(silent=True) or {}
    key = data.get("api_key", "").strip()
    if not key:
        return jsonify({"success": False, "error": "API key cannot be empty."}), 400

    env_path = BASE_DIR / ".env"
    lines = []
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

    found = False
    new_lines = []
    for line in lines:
        if line.strip().startswith("GEMINI_API_KEY="):
            new_lines.append(f"GEMINI_API_KEY={key}\n")
            found = True
        else:
            new_lines.append(line)
    if not found:
        new_lines.append(f"\nGEMINI_API_KEY={key}\n")

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    os.environ["GEMINI_API_KEY"] = key

    return jsonify({
        "success": True,
        "gemini_configured": True,
        "message": "Gemini API Key saved and activated!"
    })
