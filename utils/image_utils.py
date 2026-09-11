import io
from typing import Tuple
from PIL import Image


def validate_and_process_image(image_bytes: bytes, max_dimension: int = 2048) -> Tuple[bytes, int, int, str]:
    """
    Validates image bytes, gets dimensions and mime type,
    and scales down if exceeding max_dimension to optimize API performance.
    Returns (processed_bytes, width, height, mime_type).
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.verify()

        # Re-open after verify() because verify destroys file pointer
        image = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        raise ValueError(f"Invalid or corrupted image file: {str(e)}")

    orig_format = image.format or "JPEG"
    format_to_mime = {
        "PNG": "image/png",
        "JPEG": "image/jpeg",
        "JPG": "image/jpeg",
        "WEBP": "image/webp",
    }
    mime_type = format_to_mime.get(orig_format.upper(), "image/jpeg")

    orig_w, orig_h = image.size

    # Scale down if dimensions are huge
    if orig_w > max_dimension or orig_h > max_dimension:
        image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        save_format = "PNG" if mime_type == "image/png" else "JPEG"
        if save_format == "JPEG" and image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        image.save(buf, format=save_format, quality=90)
        return buf.getvalue(), image.width, image.height, mime_type

    return image_bytes, orig_w, orig_h, mime_type
