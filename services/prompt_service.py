class PromptService:
    @staticmethod
    def get_reconstruction_prompt(img_width: int, img_height: int) -> str:
        return f"""You are an AI visual design reconstruction engine.

Analyze the supplied image and convert its visual structure into a structured editable design representation.
The image dimensions are {img_width}x{img_height} pixels. All x, y, width, and height coordinates MUST be in this exact coordinate space.

Do not describe the image in prose.
Identify every meaningful design element.

For every text element determine:
1. Exact visible text
2. Element type ("heading", "paragraph", "text", or "button")
3. Bounding box
4. X position (left edge in pixels)
5. Y position (top edge in pixels)
6. Width (in pixels)
7. Height (in pixels)
8. Approximate font family (Choose from: "Arial", "Helvetica", "Georgia", "Times New Roman", "Inter", "Roboto", "Poppins", "Montserrat", "Open Sans", "system-ui")
9. Approximate font size (in pixels, e.g. 14, 24, 48, 72)
10. Font weight (100, 300, 400, 600, 700, 800, 900)
11. Font style ("normal" or "italic")
12. Text color (hex code e.g. "#FFFFFF", "#1E293B")
13. Text alignment ("left", "center", "right", or "justify")
14. Line height (e.g. 1.1, 1.2, 1.4)
15. Letter spacing (in pixels, e.g. 0, 1, 2)
16. Text transform ("none", "uppercase", "lowercase", or "capitalize")
17. Opacity (0.0 to 1.0)
18. Rotation (degrees, 0 if upright)

Identify non-text elements such as:
- background (canvas background or background rectangle)
- button (with background color, border radius, padding, and text content)
- rectangle (badges, cards, accent containers)
- circle (decorative icons, avatars)

Estimate:
- padding (top, right, bottom, left)
- margins (top, right, bottom, left)
- hierarchy and stacking order (zIndex)

Use pixel coordinates based on the original image dimensions ({img_width}x{img_height}).
The objective is visual reconstruction.
Do not claim that you know the original HTML/CSS.
Do not invent hidden elements.
If a property cannot be determined exactly from the raster image, provide a reasonable estimate.

Return ONLY valid JSON matching this schema:
{{
  "canvas": {{
    "width": {img_width},
    "height": {img_height},
    "background": "#HEX_COLOR"
  }},
  "elements": [
    {{
      "id": "element_001",
      "type": "heading|paragraph|text|button|rectangle|circle",
      "content": "Text here",
      "position": {{ "x": 0, "y": 0 }},
      "size": {{ "width": 100, "height": 50 }},
      "style": {{
        "fontFamily": "Inter",
        "fontSize": 32,
        "fontWeight": 700,
        "fontStyle": "normal",
        "textDecoration": "none",
        "color": "#111827",
        "backgroundColor": "transparent",
        "borderRadius": 0,
        "borderWidth": 0,
        "borderColor": "transparent",
        "textAlign": "left",
        "lineHeight": 1.2,
        "letterSpacing": 0,
        "textTransform": "none",
        "opacity": 1.0
      }},
      "layout": {{
        "padding": {{ "top": 0, "right": 0, "bottom": 0, "left": 0 }},
        "margin": {{ "top": 0, "right": 0, "bottom": 0, "left": 0 }}
      }},
      "transform": {{
        "rotation": 0
      }},
      "zIndex": 1
    }}
  ]
}}
Do not return markdown code blocks. Do not return explanations."""

    @staticmethod
    def get_ai_edit_prompt(user_request: str, current_design_json: str, selected_element_id: str) -> str:
        return f"""You are an AI design editor.

You are given an existing structured design JSON and a user request.

Modify ONLY the properties required by the user.
Do not change unrelated elements.
Do not redesign the entire composition.
Return only a valid JSON patch.

User request:
{user_request}

Current design:
{current_design_json}

Selected element:
{selected_element_id}

Return only the minimal required changes in this JSON format:
{{
  "elementId": "{selected_element_id}",
  "changes": {{
    // Only changed properties here, for example:
    // "content": "NEW TEXT",
    // "position": {{ "x": 100, "y": 120 }},
    // "size": {{ "width": 500, "height": 80 }},
    // "style": {{ "fontSize": 72, "color": "#0000FF", "fontWeight": 700 }}
  }},
  "explanation": "Brief 1-sentence note of what was changed"
}}
Do not return markdown or commentary."""
