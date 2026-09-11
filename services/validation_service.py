import json
import re
from typing import Dict, Any
from utils.file_utils import sanitize_hex_color, map_safe_font


class ValidationService:
    @staticmethod
    def extract_json_from_text(raw_text: str) -> Dict[str, Any]:
        """Extracts and parses JSON from raw LLM output, handling markdown blocks and partial text."""
        if not raw_text or not raw_text.strip():
            raise ValueError("Empty response from AI engine.")

        text = raw_text.strip()

        # Strip ```json ... ``` code fence
        if "```json" in text:
            match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
            if match:
                text = match.group(1).strip()
        elif "```" in text:
            match = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
            if match:
                text = match.group(1).strip()

        # If still surrounded by braces or text, find first { and last }
        start_idx = text.find("{")
        end_idx = text.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            text = text[start_idx:end_idx + 1]

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            # Controlled repair: remove trailing commas before closing braces/brackets
            repaired = re.sub(r",\s*([\]}])", r"\1", text)
            try:
                return json.loads(repaired)
            except json.JSONDecodeError:
                raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")

    @staticmethod
    def normalize_design_json(raw_data: Dict[str, Any], default_w: int = 1080, default_h: int = 1350) -> Dict[str, Any]:
        """Normalizes and sanitizes all properties of the design JSON against schema."""
        canvas = raw_data.get("canvas", {})
        try:
            canvas_w = int(canvas.get("width") or default_w)
        except (ValueError, TypeError):
            canvas_w = default_w

        try:
            canvas_h = int(canvas.get("height") or default_h)
        except (ValueError, TypeError):
            canvas_h = default_h

        canvas_bg = sanitize_hex_color(canvas.get("background"), "#FFFFFF")
        if canvas_bg == "invalid_color" or canvas_bg == default_w:
            canvas_bg = "#FFFFFF"

        normalized_canvas = {
            "width": max(100, min(canvas_w, 5000)),
            "height": max(100, min(canvas_h, 5000)),
            "background": canvas_bg
        }

        raw_elements = raw_data.get("elements", [])
        normalized_elements = []

        valid_types = {"text", "heading", "paragraph", "button", "rectangle", "circle", "image", "background"}
        valid_aligns = {"left", "center", "right", "justify"}
        valid_transforms = {"none", "uppercase", "lowercase", "capitalize"}

        for idx, el in enumerate(raw_elements):
            if not isinstance(el, dict):
                continue

            el_id = str(el.get("id") or f"el_{idx + 1}")
            el_type = str(el.get("type", "text")).lower()
            if el_type not in valid_types:
                el_type = "text"

            content = str(el.get("content", ""))

            # Position & Size from box_2d if available, else from position/size
            box_2d = el.get("box_2d")
            has_box = False
            if isinstance(box_2d, (list, tuple)) and len(box_2d) == 4:
                try:
                    ymin, xmin, ymax, xmax = [float(v) for v in box_2d]
                    scale = 1000.0 if max(ymin, xmin, ymax, xmax) > 1.0 else 1.0
                    pos_x = round((xmin / scale) * canvas_w)
                    pos_y = round((ymin / scale) * canvas_h)
                    width = max(10.0, round(((xmax - xmin) / scale) * canvas_w))
                    height = max(10.0, round(((ymax - ymin) / scale) * canvas_h))
                    has_box = True
                except Exception:
                    has_box = False

            if not has_box:
                pos = el.get("position", {})
                try:
                    pos_x = float(pos.get("x", 0))
                except (ValueError, TypeError):
                    pos_x = 0.0
                try:
                    pos_y = float(pos.get("y", 0))
                except (ValueError, TypeError):
                    pos_y = 0.0

                size = el.get("size", {})
                try:
                    width = max(10.0, float(size.get("width", 200)))
                except (ValueError, TypeError):
                    width = 200.0
                try:
                    height = max(10.0, float(size.get("height", 60)))
                except (ValueError, TypeError):
                    height = 60.0

            # Style
            style = el.get("style", {})
            font_family = map_safe_font(style.get("fontFamily", "Inter"))
            try:
                font_size = float(style.get("fontSize", 0))
            except (ValueError, TypeError):
                font_size = 0.0

            # Calibrate font size relative to bounding box height
            if el_type == "heading":
                expected_fs = round(height * 0.72)
                if font_size <= 10.0 or abs(font_size - expected_fs) > (height * 0.45):
                    font_size = expected_fs
            elif el_type == "button":
                expected_fs = round(height * 0.48)
                if font_size <= 8.0 or abs(font_size - expected_fs) > (height * 0.40):
                    font_size = expected_fs
            elif el_type in ("paragraph", "text"):
                if font_size <= 8.0:
                    font_size = max(14.0, min(36.0, round(height * 0.65)))

            font_size = max(8.0, min(300.0, font_size))

            try:
                font_weight = int(style.get("fontWeight", 400))
                if font_weight < 100:
                    font_weight = 400
                elif font_weight > 900:
                    font_weight = 900
            except (ValueError, TypeError):
                font_weight = 400

            font_style = "italic" if str(style.get("fontStyle", "")).lower() == "italic" else "normal"
            text_decor = str(style.get("textDecoration", "none")).lower()
            if text_decor not in {"none", "underline", "line-through"}:
                text_decor = "none"

            text_color = sanitize_hex_color(style.get("color"), "#0f172a")
            bg_color = sanitize_hex_color(style.get("backgroundColor"), "transparent")
            border_color = sanitize_hex_color(style.get("borderColor"), "transparent")

            try:
                border_radius = max(0.0, float(style.get("borderRadius", 0)))
            except (ValueError, TypeError):
                border_radius = 0.0

            try:
                border_width = max(0.0, float(style.get("borderWidth", 0)))
            except (ValueError, TypeError):
                border_width = 0.0

            text_align = str(style.get("textAlign", "left")).lower()
            if text_align not in valid_aligns:
                text_align = "left"

            # Auto-detect centered layout: if element center is near canvas center
            if text_align == "left" and el_type in ("heading", "button"):
                box_center_x = pos_x + (width / 2.0)
                canvas_center_x = canvas_w / 2.0
                if abs(box_center_x - canvas_center_x) < (canvas_w * 0.07):
                    text_align = "center"

            try:
                line_height = max(0.8, min(3.0, float(style.get("lineHeight", 1.2))))
            except (ValueError, TypeError):
                line_height = 1.2

            try:
                letter_spacing = max(-5.0, min(30.0, float(style.get("letterSpacing", 0))))
            except (ValueError, TypeError):
                letter_spacing = 0.0

            text_transform = str(style.get("textTransform", "none")).lower()
            if text_transform not in valid_transforms:
                text_transform = "none"

            try:
                opacity = max(0.0, min(1.0, float(style.get("opacity", 1.0))))
            except (ValueError, TypeError):
                opacity = 1.0

            # Layout padding & margin
            layout = el.get("layout", {})
            padding = layout.get("padding", {})
            margin = layout.get("margin", {})

            def get_box(box_dict):
                return {
                    "top": float(box_dict.get("top", 0) or 0),
                    "right": float(box_dict.get("right", 0) or 0),
                    "bottom": float(box_dict.get("bottom", 0) or 0),
                    "left": float(box_dict.get("left", 0) or 0),
                }

            # Transform rotation
            transform = el.get("transform", {})
            try:
                rotation = float(transform.get("rotation", 0))
                # Normalize rotation into [-360, 360]
                rotation = rotation % 360
            except (ValueError, TypeError):
                rotation = 0.0

            normalized_elements.append({
                "id": el_id,
                "type": el_type,
                "content": content,
                "position": {"x": pos_x, "y": pos_y},
                "size": {"width": width, "height": height},
                "style": {
                    "fontFamily": font_family,
                    "fontSize": font_size,
                    "fontWeight": font_weight,
                    "fontStyle": font_style,
                    "textDecoration": text_decor,
                    "color": text_color,
                    "backgroundColor": bg_color,
                    "borderRadius": border_radius,
                    "borderWidth": border_width,
                    "borderColor": border_color,
                    "textAlign": text_align,
                    "lineHeight": line_height,
                    "letterSpacing": letter_spacing,
                    "textTransform": text_transform,
                    "opacity": opacity,
                },
                "layout": {
                    "padding": get_box(padding),
                    "margin": get_box(margin),
                },
                "transform": {
                    "rotation": rotation,
                },
                "zIndex": int(el.get("zIndex", idx + 1)),
            })

        # Anti-collision pass on text elements
        resolved_elements = ValidationService._resolve_text_overlaps(
            normalized_elements,
            normalized_canvas["width"],
            normalized_canvas["height"]
        )

        return {
            "canvas": normalized_canvas,
            "elements": resolved_elements,
        }

    @staticmethod
    def _resolve_text_overlaps(elements: list, canvas_w: int, canvas_h: int) -> list:
        """Resolves overlapping text elements by adjusting vertical and horizontal positioning."""
        text_types = {"heading", "subheading", "paragraph", "text", "badge"}
        min_v_gap = 4
        min_h_gap = 4
        max_iters = 30

        for _ in range(max_iters):
            collision = False
            for i in range(len(elements)):
                e1 = elements[i]
                if e1.get("type") not in text_types:
                    continue
                x1, y1 = e1["position"]["x"], e1["position"]["y"]
                w1, h1 = e1["size"]["width"], e1["size"]["height"]

                for j in range(i + 1, len(elements)):
                    e2 = elements[j]
                    if e2.get("type") not in text_types:
                        continue
                    x2, y2 = e2["position"]["x"], e2["position"]["y"]
                    w2, h2 = e2["size"]["width"], e2["size"]["height"]

                    ix = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
                    iy = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))

                    if ix > 0 and iy > 0:
                        collision = True
                        if y2 + h2 / 2.0 >= y1 + h1 / 2.0:
                            e2["position"]["y"] = y1 + h1 + min_v_gap
                        else:
                            if x2 >= x1:
                                e2["position"]["x"] = min(x1 + w1 + min_h_gap, canvas_w - w2)
                            else:
                                e1["position"]["x"] = min(x2 + w2 + min_h_gap, canvas_w - w1)

            if not collision:
                break

        return elements
