import logging
from flask import Blueprint, request, jsonify
from config import Config, UPLOAD_DIR
from utils.file_utils import is_allowed_file, generate_unique_filename
from utils.image_utils import validate_and_process_image
from services.gemini_service import GeminiService
from services.reconstruction_service import ReconstructionService
from services.ocr_service import OCRService

logger = logging.getLogger(__name__)
analyze_bp = Blueprint("analyze", __name__)


@analyze_bp.route("/api/analyze", methods=["POST"])
def analyze_image():
    if "image" not in request.files:
        return jsonify({"success": False, "error": "No image file provided in request."}), 400

    file = request.files["image"]
    if not file or file.filename == "":
        return jsonify({"success": False, "error": "Selected file is empty."}), 400

    if not is_allowed_file(file.filename, Config.ALLOWED_EXTENSIONS):
        return jsonify({
            "success": False,
            "error": f"Unsupported file type. Please upload one of: {', '.join(Config.ALLOWED_EXTENSIONS).upper()}"
        }), 400

    try:
        raw_bytes = file.read()
        if len(raw_bytes) > Config.MAX_CONTENT_LENGTH:
            return jsonify({
                "success": False,
                "error": f"File size exceeds maximum allowed limit of {Config.MAX_UPLOAD_MB}MB."
            }), 400

        # Validate image content & dimensions using PIL
        processed_bytes, width, height, mime_type = validate_and_process_image(raw_bytes)

        # Save image to upload folder
        unique_name = generate_unique_filename(file.filename)
        save_path = UPLOAD_DIR / unique_name
        with open(save_path, "wb") as f:
            f.write(processed_bytes)

        image_url = f"/uploads/{unique_name}"
        force_demo = request.form.get("demo", "false").lower() in ("true", "1")

        # Determine whether to use Gemini Flash or OCR Layout Engine
        use_gemini = Config.is_gemini_configured() and not force_demo

        if use_gemini:
            try:
                gemini_service = GeminiService()
                design_json = gemini_service.reconstruct_image(
                    image_bytes=processed_bytes,
                    mime_type=mime_type,
                    img_width=width,
                    img_height=height
                )
                mode = "gemini"
            except Exception as e:
                logger.warning(f"Gemini reconstruction failed: {e}. Reconstructing layout via OCR...")
                design_json = OCRService.reconstruct_from_image(processed_bytes, width, height)
                mode = "ocr"
        else:
            # Reconstruct layout directly from the uploaded image using OCR + Computer Vision
            logger.info("Extracting actual document/design layout via OCR...")
            try:
                design_json = OCRService.reconstruct_from_image(processed_bytes, width, height)
                mode = "ocr"
            except Exception as e:
                logger.warning(f"OCR layout extraction failed: {e}. Using template fallback.")
                design_json = _generate_fallback_design(width, height)
                mode = "demo"

        return jsonify({
            "success": True,
            "mode": mode,
            "image_url": image_url,
            "original_dimensions": {
                "width": width,
                "height": height
            },
            "design": design_json
        })

    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Unexpected error in /api/analyze: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Failed to analyze image. Please try again with a clearer design."}), 500


@analyze_bp.route("/api/samples", methods=["GET"])
def list_samples():
    """Returns catalog of sample templates."""
    ReconstructionService.ensure_sample_images_exist()
    samples = ReconstructionService.get_sample_templates()
    result = []
    for s in samples:
        result.append({
            "id": s["id"],
            "title": s["title"],
            "category": s["category"],
            "description": s["description"],
            "width": s["width"],
            "height": s["height"],
            "image_url": f"/static/samples/{s['filename']}"
        })
    return jsonify({"success": True, "samples": result})


@analyze_bp.route("/api/sample/<sample_id>", methods=["GET"])
def get_sample(sample_id):
    """Loads a specific pre-packaged sample template."""
    ReconstructionService.ensure_sample_images_exist()
    samples = ReconstructionService.get_sample_templates()
    for s in samples:
        if s["id"] == sample_id:
            return jsonify({
                "success": True,
                "mode": "sample",
                "image_url": f"/static/samples/{s['filename']}",
                "original_dimensions": {
                    "width": s["width"],
                    "height": s["height"]
                },
                "design": s["design"]
            })
    return jsonify({"success": False, "error": "Sample template not found."}), 404


def _generate_fallback_design(width: int, height: int) -> dict:
    """Generates an attractive realistic design matching the uploaded image's dimensions."""
    scale_x = width / 1080.0
    scale_y = height / 1350.0

    samples = ReconstructionService.get_sample_templates()
    base_design = samples[0]["design"]

    # Scale elements proportionally to match the uploaded canvas size
    scaled_elements = []
    for el in base_design.get("elements", []):
        new_el = json_clone(el)
        new_el["position"]["x"] = round(el["position"]["x"] * scale_x)
        new_el["position"]["y"] = round(el["position"]["y"] * scale_y)
        new_el["size"]["width"] = max(20, round(el["size"]["width"] * scale_x))
        new_el["size"]["height"] = max(20, round(el["size"]["height"] * scale_y))
        new_el["style"]["fontSize"] = max(10, round(el["style"]["fontSize"] * min(scale_x, scale_y)))
        scaled_elements.append(new_el)

    return {
        "canvas": {
            "width": width,
            "height": height,
            "background": base_design["canvas"].get("background", "#0f172a")
        },
        "elements": scaled_elements
    }


def json_clone(obj):
    import json
    return json.loads(json.dumps(obj))
