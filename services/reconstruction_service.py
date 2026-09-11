from typing import Dict, Any, List
from PIL import Image, ImageDraw, ImageFont
from config import SAMPLES_DIR


class ReconstructionService:
    @staticmethod
    def generate_standalone_html(design: Dict[str, Any], title: str = "Reconstructed Design - PIXEL2EDIT") -> str:
        """Generates self-contained, standalone HTML/CSS from design JSON."""
        canvas = design.get("canvas", {})
        width = canvas.get("width", 1080)
        height = canvas.get("height", 1350)
        bg = canvas.get("background", "#ffffff")
        elements = design.get("elements", [])

        # Collect used font families
        used_fonts = set()
        for el in elements:
            font = el.get("style", {}).get("fontFamily", "Inter")
            if font not in {"system-ui", "Arial", "Helvetica", "Georgia", "Times New Roman"}:
                used_fonts.add(font.replace(" ", "+"))

        google_fonts_link = ""
        if used_fonts:
            fonts_query = "&family=".join([f"{f}:wght@300;400;600;700;800;900" for f in used_fonts])
            google_fonts_link = f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family={fonts_query}&display=swap" rel="stylesheet">'

        elements_html = []
        for el in elements:
            el_id = el.get("id", "")
            el_type = el.get("type", "text")
            content = el.get("content", "")
            pos = el.get("position", {})
            size = el.get("size", {})
            style = el.get("style", {})
            transform = el.get("transform", {})
            layout = el.get("layout", {})
            padding = layout.get("padding", {})
            z_index = el.get("zIndex", 1)

            x = pos.get("x", 0)
            y = pos.get("y", 0)
            w = size.get("width", 200)
            h = size.get("height", 60)
            rot = transform.get("rotation", 0)

            # Build style string
            css_rules = [
                "position: absolute;",
                f"left: {x}px;",
                f"top: {y}px;",
                f"width: {w}px;",
                f"height: {h}px;",
                f"font-family: '{style.get('fontFamily', 'Inter')}', sans-serif;",
                f"font-size: {style.get('fontSize', 32)}px;",
                f"font-weight: {style.get('fontWeight', 400)};",
                f"font-style: {style.get('fontStyle', 'normal')};",
                f"text-decoration: {style.get('textDecoration', 'none')};",
                f"color: {style.get('color', '#0f172a')};",
                f"background-color: {style.get('backgroundColor', 'transparent')};",
                f"border-radius: {style.get('borderRadius', 0)}px;",
                f"border: {style.get('borderWidth', 0)}px solid {style.get('borderColor', 'transparent')};",
                f"text-align: {style.get('textAlign', 'left')};",
                f"line-height: {style.get('lineHeight', 1.2)};",
                f"letter-spacing: {style.get('letterSpacing', 0)}px;",
                f"text-transform: {style.get('textTransform', 'none')};",
                f"opacity: {style.get('opacity', 1.0)};",
                f"z-index: {z_index};",
                "box-sizing: border-box;",
                "overflow: hidden;",
                "display: flex;",
                "align-items: center;",
                "word-break: break-word;",
            ]

            if padding:
                css_rules.append(
                    f"padding: {padding.get('top', 0)}px {padding.get('right', 0)}px {padding.get('bottom', 0)}px {padding.get('left', 0)}px;"
                )

            # Horizontal alignment in flex container
            align = style.get("textAlign", "left")
            if align == "center":
                css_rules.append("justify-content: center;")
            elif align == "right":
                css_rules.append("justify-content: flex-end;")
            else:
                css_rules.append("justify-content: flex-start;")

            if rot != 0:
                css_rules.append(f"transform: rotate({rot}deg);")

            style_str = " ".join(css_rules)

            # Escape HTML content
            safe_content = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")

            elements_html.append(
                f'    <div id="{el_id}" class="design-element {el_type}-element" style="{style_str}">\n'
                f'      <span>{safe_content}</span>\n'
                f'    </div>'
            )

        html_body = "\n".join(elements_html)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  {google_fonts_link}
  <style>
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}
    body {{
      background: #0f172a;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 40px 20px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: #f8fafc;
    }}
    .header-bar {{
      margin-bottom: 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
      max-width: {width}px;
    }}
    .header-title {{
      font-size: 18px;
      font-weight: 600;
      color: #94a3b8;
    }}
    .canvas-container {{
      position: relative;
      width: {width}px;
      height: {height}px;
      background: {bg};
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      overflow: hidden;
    }}
    @media (max-width: {width + 80}px) {{
      .canvas-container {{
        transform-origin: top center;
        transform: scale(calc((100vw - 40px) / {width}));
      }}
    }}
  </style>
</head>
<body>
  <div class="header-bar">
    <div class="header-title">PIXEL2EDIT Standalone Reconstruction</div>
    <div style="font-size: 13px; color: #64748b;">Canvas: {width} × {height}px</div>
  </div>
  <div class="canvas-container">
{html_body}
  </div>
</body>
</html>"""

    @staticmethod
    def get_sample_templates() -> List[Dict[str, Any]]:
        """Returns catalog of ready-to-test sample templates with realistic design JSON."""
        return [
            {
                "id": "sample_summer_sale",
                "title": "Summer Mega Sale Poster",
                "category": "E-Commerce / Poster",
                "filename": "summer_sale.png",
                "width": 1080,
                "height": 1350,
                "description": "Vibrant e-commerce promotional poster with bold headline, discount badge, CTA button, and coupon code.",
                "design": {
                    "canvas": {
                        "width": 1080,
                        "height": 1350,
                        "background": "#0f172a"
                    },
                    "elements": [
                        {
                            "id": "bg_glow",
                            "type": "rectangle",
                            "content": "",
                            "position": {"x": 90, "y": 80},
                            "size": {"width": 900, "height": 1190},
                            "style": {
                                "fontFamily": "Inter",
                                "fontSize": 16,
                                "fontWeight": 400,
                                "fontStyle": "normal",
                                "textDecoration": "none",
                                "color": "transparent",
                                "backgroundColor": "#1e293b",
                                "borderRadius": 32,
                                "borderWidth": 2,
                                "borderColor": "#334155",
                                "textAlign": "center",
                                "lineHeight": 1.0,
                                "letterSpacing": 0,
                                "textTransform": "none",
                                "opacity": 0.9
                            },
                            "layout": {"padding": {"top": 0, "right": 0, "bottom": 0, "left": 0}, "margin": {"top": 0, "right": 0, "bottom": 0, "left": 0}},
                            "transform": {"rotation": 0},
                            "zIndex": 1
                        },
                        {
                            "id": "tag_pill",
                            "type": "rectangle",
                            "content": "LIMITED TIME OFFER",
                            "position": {"x": 390, "y": 160},
                            "size": {"width": 300, "height": 48},
                            "style": {
                                "fontFamily": "Inter",
                                "fontSize": 15,
                                "fontWeight": 700,
                                "fontStyle": "normal",
                                "textDecoration": "none",
                                "color": "#38bdf8",
                                "backgroundColor": "#0369a1",
                                "borderRadius": 24,
                                "borderWidth": 1,
                                "borderColor": "#38bdf8",
                                "textAlign": "center",
                                "lineHeight": 1.2,
                                "letterSpacing": 2,
                                "textTransform": "uppercase",
                                "opacity": 1.0
                            },
                            "layout": {"padding": {"top": 6, "right": 16, "bottom": 6, "left": 16}, "margin": {"top": 0, "right": 0, "bottom": 0, "left": 0}},
                            "transform": {"rotation": 0},
                            "zIndex": 2
                        },
                        {
                            "id": "main_heading",
                            "type": "heading",
                            "content": "SUMMER MEGA SALE",
                            "position": {"x": 140, "y": 260},
                            "size": {"width": 800, "height": 130},
                            "style": {
                                "fontFamily": "Montserrat",
                                "fontSize": 68,
                                "fontWeight": 900,
                                "fontStyle": "normal",
                                "textDecoration": "none",
                                "color": "#ffffff",
                                "backgroundColor": "transparent",
                                "borderRadius": 0,
                                "borderWidth": 0,
                                "borderColor": "transparent",
                                "textAlign": "center",
                                "lineHeight": 1.1,
                                "letterSpacing": 1,
                                "textTransform": "uppercase",
                                "opacity": 1.0
                            },
                            "layout": {"padding": {"top": 0, "right": 0, "bottom": 0, "left": 0}, "margin": {"top": 0, "right": 0, "bottom": 0, "left": 0}},
                            "transform": {"rotation": 0},
                            "zIndex": 3
                        },
                        {
                            "id": "discount_badge",
                            "type": "heading",
                            "content": "UP TO 70% OFF",
                            "position": {"x": 190, "y": 420},
                            "size": {"width": 700, "height": 100},
                            "style": {
                                "fontFamily": "Poppins",
                                "fontSize": 60,
                                "fontWeight": 800,
                                "fontStyle": "normal",
                                "textDecoration": "none",
                                "color": "#fbbf24",
                                "backgroundColor": "transparent",
                                "borderRadius": 0,
                                "borderWidth": 0,
                                "borderColor": "transparent",
                                "textAlign": "center",
                                "lineHeight": 1.2,
                                "letterSpacing": 1.5,
                                "textTransform": "uppercase",
                                "opacity": 1.0
                            },
                            "layout": {"padding": {"top": 0, "right": 0, "bottom": 0, "left": 0}, "margin": {"top": 0, "right": 0, "bottom": 0, "left": 0}},
                            "transform": {"rotation": 0},
                            "zIndex": 3
                        },
                        {
                            "id": "sub_text",
                            "type": "paragraph",
                            "content": "Upgrade your lifestyle with our exclusive premium summer apparel & accessories collection.",
                            "position": {"x": 215, "y": 570},
                            "size": {"width": 650, "height": 80},
                            "style": {
                                "fontFamily": "Inter",
                                "fontSize": 24,
                                "fontWeight": 400,
                                "fontStyle": "normal",
                                "textDecoration": "none",
                                "color": "#cbd5e1",
                                "backgroundColor": "transparent",
                                "borderRadius": 0,
                                "borderWidth": 0,
                                "borderColor": "transparent",
                                "textAlign": "center",
                                "lineHeight": 1.4,
                                "letterSpacing": 0.5,
                                "textTransform": "none",
                                "opacity": 0.9
                            },
                            "layout": {"padding": {"top": 0, "right": 0, "bottom": 0, "left": 0}, "margin": {"top": 0, "right": 0, "bottom": 0, "left": 0}},
                            "transform": {"rotation": 0},
                            "zIndex": 3
                        },
                        {
                            "id": "cta_button",
                            "type": "button",
                            "content": "SHOP NOW",
                            "position": {"x": 365, "y": 720},
                            "size": {"width": 350, "height": 80},
                            "style": {
                                "fontFamily": "Inter",
                                "fontSize": 26,
                                "fontWeight": 700,
                                "fontStyle": "normal",
                                "textDecoration": "none",
                                "color": "#0f172a",
                                "backgroundColor": "#38bdf8",
                                "borderRadius": 40,
                                "borderWidth": 0,
                                "borderColor": "transparent",
                                "textAlign": "center",
                                "lineHeight": 1.2,
                                "letterSpacing": 2,
                                "textTransform": "uppercase",
                                "opacity": 1.0
                            },
                            "layout": {"padding": {"top": 16, "right": 32, "bottom": 16, "left": 32}, "margin": {"top": 0, "right": 0, "bottom": 0, "left": 0}},
                            "transform": {"rotation": 0},
                            "zIndex": 4
                        },
                        {
                            "id": "promo_code_box",
                            "type": "rectangle",
                            "content": "Use Code: SUMMER2025 at Checkout",
                            "position": {"x": 290, "y": 860},
                            "size": {"width": 500, "height": 55},
                            "style": {
                                "fontFamily": "Inter",
                                "fontSize": 18,
                                "fontWeight": 600,
                                "fontStyle": "normal",
                                "textDecoration": "none",
                                "color": "#94a3b8",
                                "backgroundColor": "#0f172a",
                                "borderRadius": 14,
                                "borderWidth": 1,
                                "borderColor": "#334155",
                                "textAlign": "center",
                                "lineHeight": 1.2,
                                "letterSpacing": 1,
                                "textTransform": "none",
                                "opacity": 1.0
                            },
                            "layout": {"padding": {"top": 8, "right": 16, "bottom": 8, "left": 16}, "margin": {"top": 0, "right": 0, "bottom": 0, "left": 0}},
                            "transform": {"rotation": 0},
                            "zIndex": 3
                        },
                        {
                            "id": "footer_note",
                            "type": "text",
                            "content": "Free worldwide shipping on all orders over $75 • 30-Day Money Back Guarantee",
                            "position": {"x": 190, "y": 1050},
                            "size": {"width": 700, "height": 40},
                            "style": {
                                "fontFamily": "Inter",
                                "fontSize": 16,
                                "fontWeight": 400,
                                "fontStyle": "normal",
                                "textDecoration": "none",
                                "color": "#64748b",
                                "backgroundColor": "transparent",
                                "borderRadius": 0,
                                "borderWidth": 0,
                                "borderColor": "transparent",
                                "textAlign": "center",
                                "lineHeight": 1.3,
                                "letterSpacing": 0.5,
                                "textTransform": "none",
                                "opacity": 0.8
                            },
                            "layout": {"padding": {"top": 0, "right": 0, "bottom": 0, "left": 0}, "margin": {"top": 0, "right": 0, "bottom": 0, "left": 0}},
                            "transform": {"rotation": 0},
                            "zIndex": 3
                        }
                    ]
                }
            },
            {
                "id": "sample_tech_summit",
                "title": "Global AI & Tech Summit",
                "category": "Conference / Event",
                "filename": "tech_summit.png",
                "width": 1080,
                "height": 1350,
                "description": "Futuristic tech conference poster featuring gradient card, date, venue, headline, and speaker registration CTA.",
                "design": {
                    "canvas": {
                        "width": 1080,
                        "height": 1350,
                        "background": "#030712"
                    },
                    "elements": [
                        {
                            "id": "conf_badge",
                            "type": "text",
                            "content": "SAN FRANCISCO • OCTOBER 24-26, 2025",
                            "position": {"x": 140, "y": 140},
                            "size": {"width": 800, "height": 40},
                            "style": {
                                "fontFamily": "Inter",
                                "fontSize": 18,
                                "fontWeight": 700,
                                "fontStyle": "normal",
                                "textDecoration": "none",
                                "color": "#a855f7",
                                "backgroundColor": "transparent",
                                "borderRadius": 0,
                                "borderWidth": 0,
                                "borderColor": "transparent",
                                "textAlign": "center",
                                "lineHeight": 1.2,
                                "letterSpacing": 3,
                                "textTransform": "uppercase",
                                "opacity": 1.0
                            },
                            "layout": {"padding": {"top": 0, "right": 0, "bottom": 0, "left": 0}, "margin": {"top": 0, "right": 0, "bottom": 0, "left": 0}},
                            "transform": {"rotation": 0},
                            "zIndex": 2
                        },
                        {
                            "id": "conf_title",
                            "type": "heading",
                            "content": "NEXT-GEN AI SUMMIT",
                            "position": {"x": 140, "y": 240},
                            "size": {"width": 800, "height": 140},
                            "style": {
                                "fontFamily": "Montserrat",
                                "fontSize": 64,
                                "fontWeight": 900,
                                "fontStyle": "normal",
                                "textDecoration": "none",
                                "color": "#f8fafc",
                                "backgroundColor": "transparent",
                                "borderRadius": 0,
                                "borderWidth": 0,
                                "borderColor": "transparent",
                                "textAlign": "center",
                                "lineHeight": 1.1,
                                "letterSpacing": 1,
                                "textTransform": "uppercase",
                                "opacity": 1.0
                            },
                            "layout": {"padding": {"top": 0, "right": 0, "bottom": 0, "left": 0}, "margin": {"top": 0, "right": 0, "bottom": 0, "left": 0}},
                            "transform": {"rotation": 0},
                            "zIndex": 2
                        },
                        {
                            "id": "conf_subtitle",
                            "type": "paragraph",
                            "content": "The premier gathering for AI researchers, ML engineers, and founders shaping autonomous intelligence.",
                            "position": {"x": 190, "y": 420},
                            "size": {"width": 700, "height": 80},
                            "style": {
                                "fontFamily": "Inter",
                                "fontSize": 22,
                                "fontWeight": 400,
                                "fontStyle": "normal",
                                "textDecoration": "none",
                                "color": "#94a3b8",
                                "backgroundColor": "transparent",
                                "borderRadius": 0,
                                "borderWidth": 0,
                                "borderColor": "transparent",
                                "textAlign": "center",
                                "lineHeight": 1.4,
                                "letterSpacing": 0.5,
                                "textTransform": "none",
                                "opacity": 0.9
                            },
                            "layout": {"padding": {"top": 0, "right": 0, "bottom": 0, "left": 0}, "margin": {"top": 0, "right": 0, "bottom": 0, "left": 0}},
                            "transform": {"rotation": 0},
                            "zIndex": 2
                        },
                        {
                            "id": "feature_card",
                            "type": "rectangle",
                            "content": "50+ KEYNOTES  •  120+ WORKSHOPS  •  5,000+ ATTENDEES",
                            "position": {"x": 190, "y": 560},
                            "size": {"width": 700, "height": 70},
                            "style": {
                                "fontFamily": "Inter",
                                "fontSize": 17,
                                "fontWeight": 700,
                                "fontStyle": "normal",
                                "textDecoration": "none",
                                "color": "#e2e8f0",
                                "backgroundColor": "#111827",
                                "borderRadius": 18,
                                "borderWidth": 1,
                                "borderColor": "#374151",
                                "textAlign": "center",
                                "lineHeight": 1.2,
                                "letterSpacing": 1.5,
                                "textTransform": "uppercase",
                                "opacity": 1.0
                            },
                            "layout": {"padding": {"top": 12, "right": 20, "bottom": 12, "left": 20}, "margin": {"top": 0, "right": 0, "bottom": 0, "left": 0}},
                            "transform": {"rotation": 0},
                            "zIndex": 2
                        },
                        {
                            "id": "conf_cta",
                            "type": "button",
                            "content": "RESERVE PASS",
                            "position": {"x": 365, "y": 700},
                            "size": {"width": 350, "height": 80},
                            "style": {
                                "fontFamily": "Inter",
                                "fontSize": 24,
                                "fontWeight": 800,
                                "fontStyle": "normal",
                                "textDecoration": "none",
                                "color": "#ffffff",
                                "backgroundColor": "#9333ea",
                                "borderRadius": 40,
                                "borderWidth": 0,
                                "borderColor": "transparent",
                                "textAlign": "center",
                                "lineHeight": 1.2,
                                "letterSpacing": 2,
                                "textTransform": "uppercase",
                                "opacity": 1.0
                            },
                            "layout": {"padding": {"top": 16, "right": 32, "bottom": 16, "left": 32}, "margin": {"top": 0, "right": 0, "bottom": 0, "left": 0}},
                            "transform": {"rotation": 0},
                            "zIndex": 3
                        }
                    ]
                }
            },
            {
                "id": "sample_artisan_coffee",
                "title": "Artisan Coffee House",
                "category": "Cafe / Food & Beverage",
                "filename": "coffee_house.png",
                "width": 1080,
                "height": 1350,
                "description": "Warm artisanal cafe promotional flyer with serif typography, freshly roasted badge, and menu highlights.",
                "design": {
                    "canvas": {
                        "width": 1080,
                        "height": 1350,
                        "background": "#1c1917"
                    },
                    "elements": [
                        {
                            "id": "cafe_badge",
                            "type": "text",
                            "content": "EST. 2018 • SINGLE ORIGIN ROASTERY",
                            "position": {"x": 190, "y": 140},
                            "size": {"width": 700, "height": 40},
                            "style": {
                                "fontFamily": "Inter",
                                "fontSize": 16,
                                "fontWeight": 600,
                                "fontStyle": "normal",
                                "textDecoration": "none",
                                "color": "#d97706",
                                "backgroundColor": "transparent",
                                "borderRadius": 0,
                                "borderWidth": 0,
                                "borderColor": "transparent",
                                "textAlign": "center",
                                "lineHeight": 1.2,
                                "letterSpacing": 3,
                                "textTransform": "uppercase",
                                "opacity": 1.0
                            },
                            "layout": {"padding": {"top": 0, "right": 0, "bottom": 0, "left": 0}, "margin": {"top": 0, "right": 0, "bottom": 0, "left": 0}},
                            "transform": {"rotation": 0},
                            "zIndex": 2
                        },
                        {
                            "id": "cafe_headline",
                            "type": "heading",
                            "content": "THE ARTISAN BREW",
                            "position": {"x": 140, "y": 230},
                            "size": {"width": 800, "height": 120},
                            "style": {
                                "fontFamily": "Georgia",
                                "fontSize": 62,
                                "fontWeight": 700,
                                "fontStyle": "normal",
                                "textDecoration": "none",
                                "color": "#fef3c7",
                                "backgroundColor": "transparent",
                                "borderRadius": 0,
                                "borderWidth": 0,
                                "borderColor": "transparent",
                                "textAlign": "center",
                                "lineHeight": 1.1,
                                "letterSpacing": 2,
                                "textTransform": "uppercase",
                                "opacity": 1.0
                            },
                            "layout": {"padding": {"top": 0, "right": 0, "bottom": 0, "left": 0}, "margin": {"top": 0, "right": 0, "bottom": 0, "left": 0}},
                            "transform": {"rotation": 0},
                            "zIndex": 2
                        },
                        {
                            "id": "cafe_sub",
                            "type": "paragraph",
                            "content": "Handcrafted espresso, slow cold brews, and fresh French pastries baked daily at sunrise.",
                            "position": {"x": 190, "y": 380},
                            "size": {"width": 700, "height": 70},
                            "style": {
                                "fontFamily": "Inter",
                                "fontSize": 22,
                                "fontWeight": 300,
                                "fontStyle": "normal",
                                "textDecoration": "none",
                                "color": "#d6d3d1",
                                "backgroundColor": "transparent",
                                "borderRadius": 0,
                                "borderWidth": 0,
                                "borderColor": "transparent",
                                "textAlign": "center",
                                "lineHeight": 1.4,
                                "letterSpacing": 0.5,
                                "textTransform": "none",
                                "opacity": 0.9
                            },
                            "layout": {"padding": {"top": 0, "right": 0, "bottom": 0, "left": 0}, "margin": {"top": 0, "right": 0, "bottom": 0, "left": 0}},
                            "transform": {"rotation": 0},
                            "zIndex": 2
                        },
                        {
                            "id": "cafe_cta",
                            "type": "button",
                            "content": "VIEW OUR MENU",
                            "position": {"x": 375, "y": 520},
                            "size": {"width": 330, "height": 75},
                            "style": {
                                "fontFamily": "Inter",
                                "fontSize": 22,
                                "fontWeight": 700,
                                "fontStyle": "normal",
                                "textDecoration": "none",
                                "color": "#1c1917",
                                "backgroundColor": "#f59e0b",
                                "borderRadius": 38,
                                "borderWidth": 0,
                                "borderColor": "transparent",
                                "textAlign": "center",
                                "lineHeight": 1.2,
                                "letterSpacing": 1.5,
                                "textTransform": "uppercase",
                                "opacity": 1.0
                            },
                            "layout": {"padding": {"top": 14, "right": 28, "bottom": 14, "left": 28}, "margin": {"top": 0, "right": 0, "bottom": 0, "left": 0}},
                            "transform": {"rotation": 0},
                            "zIndex": 3
                        }
                    ]
                }
            }
        ]

    @classmethod
    def ensure_sample_images_exist(cls):
        """Generates realistic sample reference images using Pillow so they are always available."""
        for sample in cls.get_sample_templates():
            target_path = SAMPLES_DIR / sample["filename"]
            if not target_path.exists():
                w = sample["width"]
                h = sample["height"]
                design = sample["design"]
                canvas_bg = design["canvas"].get("background", "#0f172a")

                # Parse background hex
                bg_hex = canvas_bg.lstrip("#")
                if len(bg_hex) == 6:
                    bg_rgb = tuple(int(bg_hex[i:i + 2], 16) for i in (0, 2, 4))
                else:
                    bg_rgb = (15, 23, 42)

                img = Image.new("RGB", (w, h), color=bg_rgb)
                draw = ImageDraw.Draw(img)

                # Draw decorative elements & text from design
                for el in design.get("elements", []):
                    pos = el.get("position", {})
                    size = el.get("size", {})
                    style = el.get("style", {})
                    content = el.get("content", "")

                    x = int(pos.get("x", 0))
                    y = int(pos.get("y", 0))
                    ew = int(size.get("width", 200))
                    eh = int(size.get("height", 60))

                    # Background rectangle / button
                    bg_color_str = style.get("backgroundColor", "transparent")
                    if bg_color_str and bg_color_str != "transparent":
                        clean_bg = bg_color_str.lstrip("#")
                        if len(clean_bg) == 6:
                            el_bg_rgb = tuple(int(clean_bg[i:i + 2], 16) for i in (0, 2, 4))
                            radius = int(style.get("borderRadius", 0))
                            if radius > 0:
                                draw.rounded_rectangle([x, y, x + ew, y + eh], radius=radius, fill=el_bg_rgb)
                            else:
                                draw.rectangle([x, y, x + ew, y + eh], fill=el_bg_rgb)

                    # Text
                    if content:
                        text_color_str = style.get("color", "#ffffff")
                        text_hex = text_color_str.lstrip("#")
                        if len(text_hex) == 6:
                            text_rgb = tuple(int(text_hex[i:i + 2], 16) for i in (0, 2, 4))
                        else:
                            text_rgb = (255, 255, 255)

                        font_size = int(style.get("fontSize", 24))
                        try:
                            font = ImageFont.truetype("arial.ttf", font_size)
                        except Exception:
                            font = ImageFont.load_default()

                        # Text positioning
                        text_align = style.get("textAlign", "left")
                        bbox = draw.textbbox((0, 0), content, font=font)
                        text_w = bbox[2] - bbox[0]
                        text_h = bbox[3] - bbox[1]

                        if text_align == "center":
                            tx = x + (ew - text_w) // 2
                        elif text_align == "right":
                            tx = x + ew - text_w - 10
                        else:
                            tx = x + 10

                        ty = y + (eh - text_h) // 2
                        draw.text((tx, ty), content, font=font, fill=text_rgb)

                img.save(str(target_path), "PNG")
