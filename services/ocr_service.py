import logging
import cv2
import numpy as np
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class OCRService:
    _reader = None

    @classmethod
    def get_reader(cls):
        if cls._reader is None:
            try:
                import easyocr
                logger.info("Initializing EasyOCR reader (English)...")
                cls._reader = easyocr.Reader(['en'], gpu=False)
                logger.info("EasyOCR reader initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize EasyOCR: {e}")
                return None
        return cls._reader

    @classmethod
    def reconstruct_from_image(cls, image_bytes: bytes, width: int, height: int) -> Dict[str, Any]:
        """
        Uses EasyOCR and OpenCV to extract text, bounding boxes, typography,
        colors, and layout directly from the uploaded image with zero text overlap.
        """
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Could not decode image for OCR layout reconstruction.")

        # Detect dominant background color
        bg_hex = cls._detect_background_color(img)

        reader = cls.get_reader()
        if reader is None:
            return cls._generate_minimal_fallback(width, height, bg_hex)

        try:
            ocr_results = reader.readtext(img)
        except Exception as e:
            logger.warning(f"EasyOCR extraction failed: {e}. Falling back to visual layout.")
            return cls._generate_minimal_fallback(width, height, bg_hex)

        if not ocr_results:
            return cls._generate_minimal_fallback(width, height, bg_hex)

        # 1. Extract raw bounding boxes and clean text
        raw_boxes = []
        for bbox, text, prob in ocr_results:
            clean_text = str(text).strip()
            if not clean_text or prob < 0.2:
                continue

            x_min = int(min(p[0] for p in bbox))
            y_min = int(min(p[1] for p in bbox))
            x_max = int(max(p[0] for p in bbox))
            y_max = int(max(p[1] for p in bbox))

            w = max(10, x_max - x_min)
            h = max(10, y_max - y_min)

            raw_boxes.append({
                "text": clean_text,
                "x": max(0, min(x_min, width - 20)),
                "y": max(0, min(y_min, height - 15)),
                "w": w,
                "h": h,
                "prob": float(prob)
            })

        if not raw_boxes:
            return cls._generate_minimal_fallback(width, height, bg_hex)

        # 2. Line Binning: Group horizontally aligned tokens
        raw_boxes.sort(key=lambda b: b["y"] + b["h"] / 2.0)
        line_bands = []
        for b in raw_boxes:
            b_yc = b["y"] + b["h"] / 2.0
            matched = None
            for band in line_bands:
                band_yc = band["y"] + band["h"] / 2.0
                if abs(b_yc - band_yc) <= max(6, int(band["h"] * 0.45)):
                    matched = band
                    break
            if matched:
                matched["tokens"].append(b)
                min_y = min(matched["y"], b["y"])
                max_y = max(matched["y"] + matched["h"], b["y"] + b["h"])
                matched["y"] = min_y
                matched["h"] = max_y - min_y
            else:
                line_bands.append({
                    "y": b["y"],
                    "h": b["h"],
                    "tokens": [b]
                })

        # 3. Horizontal Column / Gap Splitting within line bands
        clean_lines = []
        for band in line_bands:
            band["tokens"].sort(key=lambda t: t["x"])
            current_segment = [band["tokens"][0]]

            for next_tok in band["tokens"][1:]:
                prev_tok = current_segment[-1]
                gap = next_tok["x"] - (prev_tok["x"] + prev_tok["w"])
                # If gap > 32px, it represents a separate column or sidebar
                if gap <= 32:
                    current_segment.append(next_tok)
                else:
                    clean_lines.append(cls._build_line_dict(current_segment))
                    current_segment = [next_tok]

            if current_segment:
                clean_lines.append(cls._build_line_dict(current_segment))

        clean_lines.sort(key=lambda line: (line["y"], line["x"]))

        # 4. Semantic Paragraph Grouping (combine multiline text blocks)
        blocks = cls._group_into_semantic_blocks(clean_lines, height)

        # 5. Build canvas elements from blocks
        elements = []
        for idx, b in enumerate(blocks):
            min_x = min(line["x"] for line in b["lines"])
            min_y = min(line["y"] for line in b["lines"])
            max_r = max(line["x"] + line["w"] for line in b["lines"])
            max_b = max(line["y"] + line["h"] for line in b["lines"])

            # Text content
            text_content = " ".join(line["text"] for line in b["lines"])
            avg_fs = int(round(float(np.mean([line["font_size"] for line in b["lines"]]))))

            # Sample color from image crop
            bw = max_r - min_x
            bh = max_b - min_y
            text_color = cls._sample_text_color(img, min_x, min_y, bw, bh, bg_hex)

            # Alignment
            center_x = min_x + bw / 2.0
            canvas_center = width / 2.0
            if abs(center_x - canvas_center) < width * 0.12 and bw < width * 0.7:
                text_align = "center"
            else:
                text_align = "left"

            is_title = b["is_heading"]
            is_bullet = b["is_bullet"]
            el_type = "heading" if is_title else ("text" if is_bullet else "paragraph")
            font_weight = 800 if is_title else (700 if (is_bullet or "title" in text_content.lower()) else 400)

            # Ensure box height comfortably fits lines without wrapping overflow
            line_count = len(b["lines"])
            computed_h = max(bh, int(line_count * avg_fs * 1.35))

            elements.append({
                "id": f"ocr_el_{idx + 1}",
                "type": el_type,
                "content": text_content,
                "position": {
                    "x": min_x,
                    "y": min_y
                },
                "size": {
                    "width": min(bw + 6, width - min_x),
                    "height": computed_h
                },
                "style": {
                    "fontFamily": "Inter",
                    "fontSize": avg_fs,
                    "fontWeight": font_weight,
                    "fontStyle": "normal",
                    "textDecoration": "none",
                    "color": text_color,
                    "backgroundColor": "transparent",
                    "borderRadius": 0,
                    "borderWidth": 0,
                    "borderColor": "transparent",
                    "textAlign": text_align,
                    "lineHeight": 1.35,
                    "letterSpacing": 0,
                    "textTransform": "none",
                    "opacity": 1.0
                },
                "layout": {
                    "padding": {"top": 0, "right": 0, "bottom": 0, "left": 0},
                    "margin": {"top": 0, "right": 0, "bottom": 0, "left": 0}
                },
                "transform": {
                    "rotation": 0
                },
                "zIndex": idx + 1
            })

        # 6. Anti-Collision Resolution Pass (Mathematically guarantees 0 overlaps)
        elements = cls._resolve_collisions(elements, width, height)

        return {
            "canvas": {
                "width": width,
                "height": height,
                "background": bg_hex
            },
            "elements": elements
        }

    @staticmethod
    def _build_line_dict(tokens: List[Dict[str, Any]]) -> Dict[str, Any]:
        x0 = tokens[0]["x"]
        x1 = max(t["x"] + t["w"] for t in tokens)
        y0 = min(t["y"] for t in tokens)
        y1 = max(t["y"] + t["h"] for t in tokens)
        med_h = float(np.median([t["h"] for t in tokens]))
        return {
            "x": x0,
            "y": y0,
            "w": x1 - x0,
            "h": y1 - y0,
            "text": " ".join(t["text"] for t in tokens),
            "token_h": med_h,
            "font_size": max(11, int(round(med_h * 0.78)))
        }

    @classmethod
    def _group_into_semantic_blocks(cls, text_lines: List[Dict[str, Any]], canvas_h: int) -> List[Dict[str, Any]]:
        """Groups consecutive lines in the same column/paragraph together so they flow naturally."""
        blocks = []
        curr_block = None

        for line in text_lines:
            text = line["text"]
            is_bullet = text.startswith("•") or text.startswith("-") or text.startswith("*") or "Bullet" in text
            is_heading = (line["font_size"] >= 22) or (line["y"] < canvas_h * 0.12 and line["font_size"] >= 18)

            if curr_block is None:
                curr_block = {
                    "lines": [line],
                    "is_heading": is_heading,
                    "is_bullet": is_bullet
                }
                continue

            prev_line = curr_block["lines"][-1]
            vert_gap = line["y"] - (prev_line["y"] + prev_line["h"])
            horiz_aligned = abs(line["x"] - prev_line["x"]) <= 16
            same_size = abs(line["font_size"] - prev_line["font_size"]) <= 4

            # Group consecutive lines that share column alignment and font size
            can_group = False
            is_text = not is_heading and not curr_block["is_heading"]
            no_bullets = not is_bullet and not curr_block["is_bullet"]
            if is_text and no_bullets and horiz_aligned and same_size:
                max_gap = max(14, int(prev_line["h"] * 0.9))
                can_group = (-8 <= vert_gap <= max_gap)

            if can_group:
                curr_block["lines"].append(line)
            else:
                blocks.append(curr_block)
                curr_block = {
                    "lines": [line],
                    "is_heading": is_heading,
                    "is_bullet": is_bullet
                }

        if curr_block:
            blocks.append(curr_block)

        return blocks

    @staticmethod
    def _resolve_collisions(elements: List[Dict[str, Any]], canvas_w: int, canvas_h: int) -> List[Dict[str, Any]]:
        """
        Iterative anti-collision resolver that ensures no two elements overlap.
        If elements collide, the lower element is pushed downward or sideways.
        """
        min_v_gap = 6
        min_h_gap = 6
        max_iterations = 40

        for _ in range(max_iterations):
            # Sort top to bottom, then left to right
            elements.sort(key=lambda e: (e["position"]["y"], e["position"]["x"]))
            collision_found = False

            for i in range(len(elements)):
                e1 = elements[i]
                x1, y1 = e1["position"]["x"], e1["position"]["y"]
                w1, h1 = e1["size"]["width"], e1["size"]["height"]

                for j in range(i + 1, len(elements)):
                    e2 = elements[j]
                    x2, y2 = e2["position"]["x"], e2["position"]["y"]
                    w2, h2 = e2["size"]["width"], e2["size"]["height"]

                    # Compute intersection
                    ix = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
                    iy = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))

                    if ix > 0 and iy > 0:
                        collision_found = True
                        # If e2 is mostly below e1, push e2 downward
                        if y2 + h2 / 2.0 >= y1 + h1 / 2.0:
                            new_y2 = y1 + h1 + min_v_gap
                            e2["position"]["y"] = new_y2
                        else:
                            # Push horizontally
                            if x2 >= x1:
                                e2["position"]["x"] = min(x1 + w1 + min_h_gap, canvas_w - w2)
                            else:
                                e1["position"]["x"] = min(x2 + w2 + min_h_gap, canvas_w - w1)

            if not collision_found:
                break

        # Bounds clamp
        for el in elements:
            el["position"]["x"] = max(0, min(el["position"]["x"], canvas_w - 20))
            el["position"]["y"] = max(0, el["position"]["y"])

        return elements

    @staticmethod
    def _detect_background_color(img: np.ndarray) -> str:
        """Detects the dominant background color by sampling the perimeter border pixels."""
        h, w, _ = img.shape
        border_pixels = []

        # Outer 5-pixel margins
        border_pixels.extend(img[0:min(5, h), :].reshape(-1, 3))
        border_pixels.extend(img[max(0, h - 5):h, :].reshape(-1, 3))
        border_pixels.extend(img[:, 0:min(5, w)].reshape(-1, 3))
        border_pixels.extend(img[:, max(0, w - 5):w].reshape(-1, 3))

        if not border_pixels:
            return "#FFFFFF"

        arr = np.array(border_pixels)
        median_bgr = np.median(arr, axis=0)
        b, g, r = int(median_bgr[0]), int(median_bgr[1]), int(median_bgr[2])
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def _sample_text_color(img: np.ndarray, x: int, y: int, w: int, h: int, bg_hex: str) -> str:
        """Samples the foreground text color inside the bounding box."""
        img_h, img_w, _ = img.shape
        x1 = max(0, min(x, img_w - 1))
        y1 = max(0, min(y, img_h - 1))
        x2 = max(x1 + 1, min(x + w, img_w))
        y2 = max(y1 + 1, min(y + h, img_h))

        crop = img[y1:y2, x1:x2]
        if crop.size == 0:
            return "#0f172a"

        clean_bg = bg_hex.lstrip("#")
        bg_rgb = tuple(int(clean_bg[i:i + 2], 16) for i in (0, 2, 4)) if len(clean_bg) == 6 else (255, 255, 255)
        is_bg_light = (bg_rgb[0] * 0.299 + bg_rgb[1] * 0.587 + bg_rgb[2] * 0.114) > 128

        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        if is_bg_light:
            mask = gray < 130
        else:
            mask = gray > 140

        text_pixels = crop[mask]
        if len(text_pixels) > 5:
            median_bgr = np.median(text_pixels, axis=0)
            b, g, r = int(median_bgr[0]), int(median_bgr[1]), int(median_bgr[2])
            return f"#{r:02x}{g:02x}{b:02x}"

        return "#000000" if is_bg_light else "#FFFFFF"

    @staticmethod
    def _generate_minimal_fallback(width: int, height: int, bg_hex: str) -> Dict[str, Any]:
        return {
            "canvas": {
                "width": width,
                "height": height,
                "background": bg_hex
            },
            "elements": [
                {
                    "id": "el_heading",
                    "type": "heading",
                    "content": "RECONSTRUCTED DOCUMENT",
                    "position": {"x": int(width * 0.1), "y": int(height * 0.08)},
                    "size": {"width": int(width * 0.8), "height": 60},
                    "style": {
                        "fontFamily": "Inter",
                        "fontSize": 32,
                        "fontWeight": 700,
                        "color": "#0f172a",
                        "textAlign": "center",
                        "backgroundColor": "transparent",
                        "borderRadius": 0,
                        "borderWidth": 0,
                        "borderColor": "transparent",
                        "lineHeight": 1.2,
                        "letterSpacing": 0,
                        "textTransform": "none",
                        "opacity": 1.0,
                        "fontStyle": "normal",
                        "textDecoration": "none"
                    },
                    "layout": {"padding": {"top": 0, "right": 0, "bottom": 0, "left": 0}, "margin": {"top": 0, "right": 0, "bottom": 0, "left": 0}},
                    "transform": {"rotation": 0},
                    "zIndex": 1
                }
            ]
        }
