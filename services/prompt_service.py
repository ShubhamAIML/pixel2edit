class PromptService:
    @staticmethod
    def get_reconstruction_prompt(img_width: int, img_height: int) -> str:
        return f"""You are an expert AI visual design reconstruction engine.

Analyze the supplied image and convert its visual structure into a precise editable design representation.
The image dimensions are {img_width}x{img_height} pixels.

CRITICAL INSTRUCTIONS FOR SPATIAL POSITIONING & FONT SIZING:
1. For EVERY element, detect its PRECISE 2D bounding box as "box_2d": [ymin, xmin, ymax, xmax] on a normalized 0 to 1000 scale (where 0 is top/left and 1000 is bottom/right).
2. Calculate position: x = round((xmin / 1000) * {img_width}), y = round((ymin / 1000) * {img_height}).
3. Calculate size: width = round(((xmax - xmin) / 1000) * {img_width}), height = round(((ymax - ymin) / 1000) * {img_height}).
4. FONT SIZE CALIBRATION (in pixels):
   - Accurately match the visual glyph height inside the bounding box.
   - For single-line headings and titles: fontSize should be ~70% to 80% of bounding box height.
   - For buttons and badges: fontSize should be ~45% to 55% of the button height (accounting for padding).
   - For body text / paragraphs: estimate actual rendered font size (e.g. 14, 16, 18, 20, 24).
5. TEXT ALIGNMENT:
   - If the text is centered within the canvas or within its container/button, set "textAlign": "center".
   - If aligned to the left edge, set "textAlign": "left".
   - If aligned to the right edge, set "textAlign": "right".

Identify every meaningful design element:
- text elements: "heading", "paragraph", "text"
- UI components: "button" (with background color, border radius, padding, text content)
- shapes: "rectangle" (background cards, badges, banners), "circle" (icons, avatars)

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
      "content": "Exact visible text here",
      "box_2d": [ymin, xmin, ymax, xmax],
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
        "textAlign": "center",
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
