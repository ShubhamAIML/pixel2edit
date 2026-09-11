import logging
from flask import Flask, render_template, send_from_directory, jsonify
from config import Config
from routes.health import health_bp
from routes.analyze import analyze_bp
from routes.ai_edit import ai_edit_bp
from routes.export import export_bp
from services.reconstruction_service import ReconstructionService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("pixel2edit")


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )
    app.config.from_object(Config)

    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(analyze_bp)
    app.register_blueprint(ai_edit_bp)
    app.register_blueprint(export_bp)

    # Serve user uploaded files safely
    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        return send_from_directory(Config.UPLOAD_FOLDER, filename)

    # Main landing page
    @app.route("/")
    def index():
        return render_template(
            "index.html",
            gemini_configured=Config.is_gemini_configured(),
            model_name=Config.get_gemini_model()
        )

    # Error Handlers
    @app.errorhandler(413)
    def file_too_large(e):
        return jsonify({
            "success": False,
            "error": (
                f"File is too large. Maximum allowed size is "
                f"{Config.MAX_UPLOAD_MB}MB."
            )
        }), 413

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Internal server error: {e}")
        return jsonify({
            "success": False,
            "error": "An internal server error occurred."
        }), 500

    # Ensure sample images exist on disk for immediate 1-click demos
    try:
        ReconstructionService.ensure_sample_images_exist()
        logger.info("Sample reference images verified.")
    except Exception as e:
        logger.warning(f"Could not pre-generate sample images: {e}")

    return app


app = create_app()


if __name__ == "__main__":
    host = Config.HOST
    logger.info(
        f"Starting PIXEL2EDIT on http://{host}:{Config.PORT} "
        f"(Debug: {Config.DEBUG})"
    )
    app.run(
        host=host,
        port=Config.PORT,
        debug=Config.DEBUG,
        use_reloader=False
    )
