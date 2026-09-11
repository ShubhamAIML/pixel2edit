import logging
import re
from flask import Blueprint, request, jsonify
from config import Config
from services.gemini_service import GeminiService

logger = logging.getLogger(__name__)
ai_edit_bp = Blueprint("ai_edit", __name__)

COLOR_NAME_MAP = {
    "blue": "#38bdf8",
    "deep blue": "#1d4ed8",
    "navy": "#1e3a8a",
    "neon blue": "#00f0ff",
    "cyan": "#06b6d4",
    "red": "#ef4444",
    "crimson": "#dc2626",
    "green": "#22c55e",
    "emerald": "#10b981",
    "yellow": "#eab308",
    "amber": "#f59e0b",
    "gold": "#fbbf24",
    "purple": "#a855f7",
    "violet": "#8b5cf6",
    "pink": "#ec4899",
    "white": "#ffffff",
    "black": "#000000",
    "gray": "#94a3b8",
    "orange": "#f97316",
}


@ai_edit_bp.route("/api/ai-edit", methods=["POST"])
def ai_edit():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid JSON body in request."}), 400

    instruction = (data.get("instruction") or "").strip()
    if not instruction:
        return jsonify({"success": False, "error": "Please provide an edit instruction for the AI."}), 400

    design = data.get("design")
    if not design or "elements" not in design:
        return jsonify({"success": False, "error": "No design state provided."}), 400

    selected_id = data.get("selected_element_id")
    elements = design.get("elements", [])
    selected_el = None

    if selected_id:
        for el in elements:
            if el.get("id") == selected_id:
                selected_el = el
                break

    # If no specific element selected, default to first heading or first element
    if not selected_el and elements:
        for el in elements:
            if el.get("type") in ("heading", "text"):
                selected_el = el
                selected_id = el.get("id")
                break
        if not selected_el:
            selected_el = elements[0]
            selected_id = selected_el.get("id")

    if not selected_el:
        return jsonify({"success": False, "error": "No elements found in current design to edit."}), 400

    # Determine whether to call Gemini or use intelligent local fallback
    if Config.is_gemini_configured():
        try:
            gemini_service = GeminiService()
            patch = gemini_service.edit_with_ai(
                user_instruction=instruction,
                current_design=design,
                selected_element_id=selected_id
            )
            return jsonify({
                "success": True,
                "mode": "gemini",
                "patch": patch
            })
        except Exception as e:
            logger.warning(f"Gemini AI edit failed: {e}. Using local intelligence fallback.")
            patch = _generate_local_heuristic_patch(instruction, selected_el)
            return jsonify({
                "success": True,
                "mode": "fallback",
                "patch": patch
            })
    else:
        # Demo / Offline mode heuristic patch
        patch = _generate_local_heuristic_patch(instruction, selected_el)
        return jsonify({
            "success": True,
            "mode": "demo",
            "patch": patch
        })


def _generate_local_heuristic_patch(instruction: str, element: dict) -> dict:
    """Parses natural language instruction locally when API key is not present or offline."""
    lower = instruction.lower()
    changes = {"style": {}}
    explanation_parts = []

    current_style = element.get("style", {})

    # 1. Size / Font size
    if "bigger" in lower or "larger" in lower or "increase" in lower:
        curr_fs = float(current_style.get("fontSize", 32))
        new_fs = min(160, round(curr_fs * 1.3))
        changes["style"]["fontSize"] = new_fs
        explanation_parts.append(f"Increased font size to {new_fs}px")
    elif "smaller" in lower or "decrease" in lower or "reduce" in lower:
        curr_fs = float(current_style.get("fontSize", 32))
        new_fs = max(12, round(curr_fs * 0.75))
        changes["style"]["fontSize"] = new_fs
        explanation_parts.append(f"Decreased font size to {new_fs}px")

    # 2. Color
    for color_name, hex_val in COLOR_NAME_MAP.items():
        if re.search(r"\b" + re.escape(color_name) + r"\b", lower):
            changes["style"]["color"] = hex_val
            explanation_parts.append(f"Changed color to {color_name} ({hex_val})")
            break

    # 3. Bold / Weight
    if "bold" in lower:
        changes["style"]["fontWeight"] = 800
        explanation_parts.append("Made text bold")
    elif "light" in lower or "thin" in lower:
        changes["style"]["fontWeight"] = 300
        explanation_parts.append("Made text lighter weight")

    # 4. Italic
    if "italic" in lower or "slanted" in lower:
        changes["style"]["fontStyle"] = "italic"
        explanation_parts.append("Applied italic style")
    elif "normal" in lower and "style" in lower:
        changes["style"]["fontStyle"] = "normal"

    # 5. Underline
    if "underline" in lower:
        changes["style"]["textDecoration"] = "underline"
        explanation_parts.append("Underlined text")

    # 6. Alignment
    if "center" in lower:
        changes["style"]["textAlign"] = "center"
        explanation_parts.append("Centered text alignment")
    elif "right" in lower:
        changes["style"]["textAlign"] = "right"
        explanation_parts.append("Right aligned text")
    elif "left" in lower:
        changes["style"]["textAlign"] = "left"
        explanation_parts.append("Left aligned text")

    # 7. Text Transform
    if "uppercase" in lower or "capital" in lower:
        changes["style"]["textTransform"] = "uppercase"
        explanation_parts.append("Converted to uppercase")
    elif "lowercase" in lower:
        changes["style"]["textTransform"] = "lowercase"
        explanation_parts.append("Converted to lowercase")

    # 8. Direct text change (e.g., 'change text to "Summer Festival"')
    quotes_match = re.search(r'["\']([^"\']+)["\']', instruction)
    if quotes_match:
        new_text = quotes_match.group(1)
        changes["content"] = new_text
        explanation_parts.append(f'Updated text to "{new_text}"')

    # If no changes were parsed, default to a notable stylish upgrade
    if not changes["style"] and "content" not in changes:
        changes["style"]["fontSize"] = round(float(current_style.get("fontSize", 32)) * 1.25)
        changes["style"]["color"] = "#38bdf8"
        explanation_parts.append("Enhanced styling and highlighted in vibrant blue")

    return {
        "elementId": element.get("id"),
        "changes": changes,
        "explanation": "; ".join(explanation_parts) if explanation_parts else "Applied AI adjustments."
    }
