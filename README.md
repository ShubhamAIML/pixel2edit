# PIXEL2EDIT

> **"Turn an image into an editable design."**

PIXEL2EDIT is a full-stack AI-assisted visual design reconstruction platform built with Python, Flask, and Google Gemini Flash multimodal vision. It takes any flattened raster image (poster, flyer, advertisement, social media graphic, or UI mockup) and converts it into a structured, editable web-based canvas displayed side-by-side with the original reference image.

---

## 1. Project Overview

Raster images (PNG, JPG, WEBP) lack layers, editable typography, CSS rules, and component hierarchies. PIXEL2EDIT bridges this gap using Google Gemini Flash vision reasoning:

```
        ORIGINAL IMAGE
              ↓
     GEMINI FLASH VISION
              ↓
     DESIGN UNDERSTANDING
              ↓
    STRUCTURED DESIGN JSON
              ↓
    HTML/CSS RECONSTRUCTION
              ↓
    EDITABLE DESIGN CANVAS
```

### Core Philosophy: AI-Assisted Visual Reconstruction
PIXEL2EDIT performs **visual reconstruction**. It does not falsely claim to recover original closed-source proprietary code or vector layers. Instead, it measures layout geometry, estimates typography, matches safe web fonts, and presents an interactive DOM canvas where every element can be edited, moved, resized, restyled, or altered using natural-language AI prompts.

---

## 2. Key Features

- **Side-by-Side Verification Workspace**:
  - **Left**: Untouched original reference image.
  - **Right**: Fully interactive, reconstructed DOM canvas with fixed coordinate resolution matching the original image (e.g. 1080×1350).
- **Overlay Comparison Mode**:
  - Lay the original image directly over the editable canvas with a live opacity slider (0–100%) to verify alignment fidelity.
- **Top Formatting Toolbar**:
  - **Typography**: Bold (`B`), Italic (`I`), Underline (`U`).
  - **Safe Web Fonts**: Arial, Helvetica, Georgia, Times New Roman, Inter, Roboto, Poppins, Montserrat, Open Sans, system-ui.
  - **Font Size**: Numeric stepper with live recalculation.
  - **Colors**: Dual color pickers with visual swatches for text color and background/fill color.
  - **Alignment**: Left, Center, Right, Justify.
  - **Styling**: Line height, letter spacing, text-transform (UPPERCASE, lowercase, Capitalize).
- **Interactive Canvas Manipulations**:
  - **Drag-to-Move**: Real-time dragging with viewport scale compensation.
  - **8-Point Resize Handles**: Resize bounding box (NW, N, NE, E, SE, S, SW, W).
  - **Double-Click Inline Editing**: Direct inline contenteditable text modification.
  - **Pixel Precision Nudging**: Arrow keys (and Shift+Arrow for 10px).
- **Property Inspector (Right Panel)**:
  - Precise geometry controls (X, Y, Width, Height).
  - Layout controls (Padding & Margin: Top, Right, Bottom, Left).
  - Appearance controls (Corner radius, border width, border color, opacity, rotation angle).
  - Layer hierarchy controls (Bring to Front, Send to Back).
- **✨ Edit with AI (Natural Language Patching)**:
  - Instruct the AI in plain English: *"Make the headline bigger, bold, and neon blue."*
  - Gemini Flash generates a **minimal JSON patch** targeting the selected element rather than re-synthesizing the entire design.
- **Undo / Redo History Stack**:
  - Keyboard shortcuts (`Ctrl+Z`, `Ctrl+Y`, `Ctrl+Shift+Z`) and toolbar actions.
- **Instant Demo Gallery**:
  - Pre-packaged, production-grade templates (Summer Sale Poster, Next-Gen AI Summit Flyer, Artisan Coffee House Card) for instant 1-click demonstration even without an image file at hand.
- **Mock Demo Mode**:
  - Automatic fallback when `GEMINI_API_KEY` is not provided, ensuring seamless evaluation and demonstration.
- **Export Capabilities**:
  - **Standalone HTML & CSS**: Zero-dependency, downloadable self-contained HTML file.
  - **Design JSON**: Raw structured data matching schema.
  - **High-Res PNG**: Client-side canvas snapshot.

---

## 3. Architecture & Single Source of Truth

PIXEL2EDIT follows a strict unidirectional reactive state pattern:

```
                  designState (JSON)
                           │
        ┌──────────────────┼──────────────────┐
        ↓                  ↓                  ↓
  Canvas Elements       Toolbar           Inspector
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ↓
                     User Actions
           (Drag, Inline Edit, AI Patch)
                           ↓
                  Updated designState
```

The DOM is never treated as the primary storage; `designState` is the sole source of truth.

---

## 4. Google Gemini Integration

- **SDK**: Current official `google-genai` Python SDK (`from google import genai`).
- **Provider**: Google Gemini Flash exclusively (`gemini-2.5-flash` or `gemini-1.5-flash`).
- **Security**: The Gemini API key remains strictly server-side in Python/Flask and is never exposed to client-side JavaScript.
- **Structured Output**: Uses Gemini's native `response_mime_type="application/json"` to guarantee structured JSON output.
- **Two Focused Prompts**:
  1. **Visual Reconstruction Prompt**: Analyzes full image bytes, extracting canvas bounds, typography metrics, bounding boxes, and styles.
  2. **AI Edit Prompt**: Accepts current design context, selected element ID, and user request to emit a minimal property patch.

---

## 5. Installation & Setup

### Prerequisites
- Python 3.10+ (Tested on Python 3.12)
- Modern web browser (Chrome, Edge, Firefox, Safari)

### Step 1: Clone or Navigate to Directory
```bash
cd c:/Users/skshi/Desktop/PIXEL2EDIT
```

### Step 2: Create and Activate Virtual Environment
**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 6. Environment Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` to configure your Gemini API credentials:

```ini
# Google Gemini API Key from https://aistudio.google.com/
GEMINI_API_KEY=your_google_gemini_api_key_here

# Flash model identifier
GEMINI_MODEL=gemini-2.5-flash

# Server settings
FLASK_PORT=5000
FLASK_DEBUG=True
MAX_UPLOAD_MB=10
```

> **Note on Demo Mode**: If `GEMINI_API_KEY` is left blank, the application automatically runs in **Mock Demo Mode**. You can still upload images or select pre-configured gallery templates and test all editing, styling, dragging, AI editing, and export features.

---

## 7. Running Locally

Start the Flask application:

```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 8. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web application home interface |
| `GET` | `/api/health` | Health check & API key configuration status |
| `POST` | `/api/analyze` | Accepts `multipart/form-data` with `image`; returns structured design JSON |
| `GET` | `/api/samples` | Lists available pre-packaged demo templates |
| `GET` | `/api/sample/<sample_id>` | Loads a specific demo template |
| `POST` | `/api/ai-edit` | Accepts natural language prompt + current design JSON; returns minimal property patch |
| `POST` | `/api/export/html` | Generates standalone downloadable HTML file |
| `POST` | `/api/export/json` | Returns formatted design JSON file download |
| `GET` | `/uploads/<filename>` | Serves uploaded reference images safely |

---

## 9. Project Structure

```
PIXEL2EDIT/
├── app.py                     # Flask application entry point
├── config.py                  # Application settings & environment loader
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
├── .env                       # Local environment file
├── README.md                  # Complete documentation
│
├── schemas/
│   └── design_schema.py       # Pydantic models & JSON schema
│
├── services/
│   ├── gemini_service.py      # Google Gemini Flash multimodal integration
│   ├── reconstruction_service.py # HTML/CSS generation & demo samples
│   ├── validation_service.py  # JSON repair, schema sanitizer & normalizer
│   └── prompt_service.py      # Strict system prompts (Sections 17 & 33)
│
├── routes/
│   ├── __init__.py
│   ├── health.py              # Health check endpoint
│   ├── analyze.py             # Image upload & Gemini reconstruction
│   ├── ai_edit.py             # Natural language design patcher
│   └── export.py              # Standalone HTML & JSON downloaders
│
├── utils/
│   ├── image_utils.py         # Pillow image validation & dimensions
│   └── file_utils.py          # Secure filenames & safe font mapping
│
├── templates/
│   └── index.html             # Single-page application shell
│
├── static/
│   ├── css/
│   │   ├── style.css          # Design system, landing page, animations
│   │   └── editor.css         # Split workspace, canvas, toolbar, inspector
│   │
│   ├── js/
│   │   ├── app.js             # Main orchestrator & dropzone logic
│   │   ├── editor.js          # Canvas engine, dragging, selection, undo/redo
│   │   ├── toolbar.js         # Top formatting toolbar controls
│   │   ├── inspector.js       # Right-side property inspector
│   │   ├── ai_edit.js         # "Edit with AI" modal handler
│   │   └── export.js          # Export to HTML, JSON, PNG
│   │
│   └── samples/               # Generated sample reference images
│
├── tests/
│   └── test_backend.py        # Automated backend test suite
│
└── uploads/                   # Stored user-uploaded images
```

---

## 10. Known Limitations

- **Raster Image Flattening**: Flattened images do not embed exact font files, CSS margins, or vector paths. The AI provides an estimate that visually mimics the original.
- **Complex Gradients & Shadows**: Multi-stop CSS mesh gradients or 3D drop-shadows are approximated using primary container backgrounds and accent colors.
- **Embedded Raster Artwork**: Embedded photographic illustrations inside a flyer are currently bounded as visual rectangular elements.

---

## 11. Future Roadmap

- **Phase 2**: Hybrid OCR + Gemini pipeline with OpenCV layout bounding box contour detection.
- **Phase 3**: Screenshot to responsive React/Tailwind code generator.
- **Phase 4**: Figma (.fig) and Canva export integrations.
- **Phase 5**: Visual similarity optimization loop using headless Chromium diff calculation.

---

## 12. Verification & Testing

To run the automated test suite:

```bash
pytest tests/test_backend.py -v
```
