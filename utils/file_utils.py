import uuid
import re
from werkzeug.utils import secure_filename

SAFE_FONT_FAMILIES = {
    "Arial", "Helvetica", "Georgia", "Times New Roman",
    "Inter", "Roboto", "Poppins", "Montserrat", "Open Sans", "Outfit",
    "Playfair Display", "Oswald", "Bebas Neue", "Lora", "Merriweather", "Cinzel",
    "system-ui"
}


def is_allowed_file(filename: str, allowed_extensions: set) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def generate_unique_filename(original_filename: str) -> str:
    cleaned = secure_filename(original_filename)
    extension = cleaned.rsplit(".", 1)[1].lower() if "." in cleaned else "png"
    unique_id = uuid.uuid4().hex[:12]
    return f"design_{unique_id}.{extension}"


def sanitize_hex_color(color_val: str, default: str = "#000000") -> str:
    if not color_val:
        return default
    color_val = str(color_val).strip()
    if color_val.lower() == "transparent":
        return "transparent"
    if re.match(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$", color_val):
        return color_val
    if re.match(r"^rgba?\([^)]+\)$", color_val):
        return color_val
    return default


def map_safe_font(font_name: str) -> str:
    if not font_name:
        return "Inter"
    font_clean = font_name.strip()
    for safe in SAFE_FONT_FAMILIES:
        if safe.lower() == font_clean.lower():
            return safe
        if safe.lower() in font_clean.lower():
            return safe

    lower = font_clean.lower()
    # Intelligent heuristics for fonts
    if "bebas" in lower:
        return "Bebas Neue"
    if "oswald" in lower:
        return "Oswald"
    if "playfair" in lower:
        return "Playfair Display"
    if "cinzel" in lower:
        return "Cinzel"
    if "lora" in lower:
        return "Lora"
    if "merriweather" in lower:
        return "Merriweather"
    if "outfit" in lower:
        return "Outfit"
    if "montserrat" in lower:
        return "Montserrat"
    if "poppins" in lower:
        return "Poppins"
    if "roboto" in lower:
        return "Roboto"
    if "open" in lower:
        return "Open Sans"
    if "serif" in lower:
        return "Playfair Display"
    if "mono" in lower or "code" in lower:
        return "system-ui"
    if "display" in lower or "title" in lower or "poster" in lower:
        return "Montserrat"
    return "Inter"

