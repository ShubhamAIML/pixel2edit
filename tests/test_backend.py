import io
import pytest
from PIL import Image
from app import create_app
from services.validation_service import ValidationService


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def create_test_image_bytes(width=800, height=600, color=(30, 41, 59)):
    from PIL import ImageDraw
    buf = io.BytesIO()
    img = Image.new("RGB", (width, height), color=color)
    draw = ImageDraw.Draw(img)
    draw.text((50, 50), "HELLO WORLD HEADLINE", fill=(255, 255, 255))
    img.save(buf, format="PNG")
    return buf.getvalue()


class TestPixel2EditBackend:
    def test_health_check(self, client):
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "ok"
        assert data["app"] == "PIXEL2EDIT"
        assert "gemini_configured" in data
        assert "model" in data

    def test_list_samples(self, client):
        res = client.get("/api/samples")
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert len(data["samples"]) >= 3

    def test_get_specific_sample(self, client):
        res = client.get("/api/sample/sample_summer_sale")
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert "design" in data
        assert data["design"]["canvas"]["width"] == 1080
        assert len(data["design"]["elements"]) > 0

    def test_upload_missing_file(self, client):
        res = client.post("/api/analyze", data={})
        assert res.status_code == 400
        assert res.get_json()["success"] is False

    def test_upload_invalid_extension(self, client):
        data = {
            "image": (io.BytesIO(b"fake data"), "test.exe")
        }
        res = client.post("/api/analyze", data=data, content_type="multipart/form-data")
        assert res.status_code == 400
        assert "Unsupported file type" in res.get_json()["error"]

    def test_upload_corrupted_image(self, client):
        data = {
            "image": (io.BytesIO(b"not a valid image content"), "test.png")
        }
        res = client.post("/api/analyze", data=data, content_type="multipart/form-data")
        assert res.status_code == 400
        assert "Invalid or corrupted image" in res.get_json()["error"]

    def test_upload_valid_image(self, client):
        img_bytes = create_test_image_bytes(width=600, height=800)
        data = {
            "image": (io.BytesIO(img_bytes), "sample_poster.png")
        }
        res = client.post("/api/analyze", data=data, content_type="multipart/form-data")
        assert res.status_code == 200
        res_json = res.get_json()
        assert res_json["success"] is True
        assert "design" in res_json
        assert "image_url" in res_json
        assert res_json["design"]["canvas"]["width"] == 600
        assert res_json["design"]["canvas"]["height"] == 800
        assert len(res_json["design"]["elements"]) > 0

    def test_ai_edit_endpoint(self, client):
        design = {
            "canvas": {"width": 1080, "height": 1350, "background": "#000000"},
            "elements": [
                {
                    "id": "text_001",
                    "type": "heading",
                    "content": "TEST HEADLINE",
                    "position": {"x": 100, "y": 100},
                    "size": {"width": 600, "height": 80},
                    "style": {
                        "fontSize": 40,
                        "color": "#ffffff",
                        "fontFamily": "Inter"
                    }
                }
            ]
        }
        payload = {
            "instruction": "Make the headline bigger and blue",
            "design": design,
            "selected_element_id": "text_001"
        }
        res = client.post("/api/ai-edit", json=payload)
        assert res.status_code == 200
        res_json = res.get_json()
        assert res_json["success"] is True
        patch = res_json["patch"]
        assert patch["elementId"] == "text_001"
        # Should have updated font size and color
        assert patch["changes"]["style"]["fontSize"] > 40
        assert patch["changes"]["style"]["color"] != "#ffffff"

    def test_export_html_endpoint(self, client):
        design = {
            "canvas": {"width": 1080, "height": 1350, "background": "#0f172a"},
            "elements": [
                {
                    "id": "h1",
                    "type": "heading",
                    "content": "SUMMER SALE",
                    "position": {"x": 100, "y": 100},
                    "size": {"width": 800, "height": 100},
                    "style": {"fontSize": 64, "color": "#ffffff", "fontFamily": "Montserrat"}
                }
            ]
        }
        res = client.post("/api/export/html", json={"design": design})
        assert res.status_code == 200
        assert res.mimetype == "text/html"
        assert b"<!DOCTYPE html>" in res.data
        assert b"SUMMER SALE" in res.data

    def test_export_json_endpoint(self, client):
        design = {
            "canvas": {"width": 1080, "height": 1350, "background": "#ffffff"},
            "elements": []
        }
        res = client.post("/api/export/json", json={"design": design})
        assert res.status_code == 200
        assert res.mimetype == "application/json"
        data = res.get_json()
        assert data["canvas"]["width"] == 1080

    def test_validation_and_normalization(self):
        malformed = {
            "canvas": {"width": "not_a_number", "background": "invalid_color"},
            "elements": [
                {
                    "id": "",
                    "type": "unknown_type",
                    "content": "Hello World",
                    "position": {"x": "120.5", "y": None},
                    "size": {"width": "-50", "height": "60"},
                    "style": {
                        "fontSize": "9999",
                        "fontWeight": 50,
                        "color": "transparent",
                        "fontFamily": "UnknownRareFont"
                    }
                }
            ]
        }
        normalized = ValidationService.normalize_design_json(malformed, default_w=1080, default_h=1350)
        assert normalized["canvas"]["width"] == 1080
        assert normalized["canvas"]["background"] == "#FFFFFF"
        el = normalized["elements"][0]
        assert el["type"] == "text"
        assert el["position"]["x"] == 120.5
        assert el["position"]["y"] == 0.0
        assert el["size"]["width"] >= 10.0
        assert el["style"]["fontSize"] <= 300.0
        assert el["style"]["fontWeight"] == 400
        assert el["style"]["fontFamily"] == "Inter"

    def test_anti_collision_resolution(self):
        """Verify that overlapping text elements are repositioned so they do not collide."""
        overlapping_design = {
            "canvas": {"width": 800, "height": 600, "background": "#ffffff"},
            "elements": [
                {
                    "id": "el_1",
                    "type": "heading",
                    "content": "Line 1 Header",
                    "position": {"x": 50, "y": 50},
                    "size": {"width": 200, "height": 40},
                },
                {
                    "id": "el_2",
                    "type": "paragraph",
                    "content": "Line 2 Paragraph",
                    "position": {"x": 50, "y": 60},  # Direct collision with el_1
                    "size": {"width": 200, "height": 30},
                }
            ]
        }
        normalized = ValidationService.normalize_design_json(overlapping_design)
        e1 = normalized["elements"][0]
        e2 = normalized["elements"][1]

        # e2 must have been pushed below e1
        assert e2["position"]["y"] >= e1["position"]["y"] + e1["size"]["height"]
