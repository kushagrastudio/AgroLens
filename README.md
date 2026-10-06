# AgroLens 🌾

Offline-capable crop disease detection for Indian smallholder farmers.
Upload a photo, get disease diagnosis, treatment steps, and government scheme information — no internet required for inference.

Built for **IEEE Hackathon 2025 — Gen AI & ML Track — PS 03.1 Vision in the Wild**

---

## What it does

- Detects crop disease from a photo using EfficientNet-B0 (ONNX, runs on-device)
- Generates Grad-CAM heatmap showing which part of the leaf the model focused on
- Retrieves treatment steps from ICAR and TNAU guidelines using local FAISS RAG
- Matches detected disease to eligible government schemes (PMFBY, PM-KISAN, etc.)
- Supports 12 Indian languages
- Works offline — only Claude API call requires internet

---

## Project Structure
agrolens/
├── backend/
│ ├── main.py # FastAPI entry point
│ ├── vision/
│ │ ├── classifier.py # EfficientNet-B0 ONNX inference
│ │ └── gradcam.py # Grad-CAM heatmap generation
│ ├── knowledge/
│ │ ├── treatment_rag.py # FAISS RAG for disease treatment
│ │ ├── scheme_finder.py # Government scheme retrieval
│ │ └── indexes/ # Built FAISS indexes (auto-generated)
│ └── models/ # ONNX model files (auto-downloaded)
├── data/
│ ├── diseases.json # Disease corpus (20 entries)
│ └── schemes.json # Government schemes (12 entries)
├── frontend/
│ ├── src/
│ │ ├── App.jsx # Main React app
│ │ └── components/
│ │ ├── Camera.jsx # Live camera capture
│ │ ├── ResultCard.jsx # Disease result display
│ │ └── HeatmapOverlay.jsx # Grad-CAM toggle overlay
│ ├── index.html
│ └── package.json
├── scripts/
│ ├── download_model.py # Downloads and exports ONNX model
│ └── build_indexes.py # Builds FAISS indexes from JSON data
├── .env.example
├── requirements.txt
└── setup.sh

---

## Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- Anthropic API key

### Install

```bash
# clone the repo
git clone https://github.com/your-username/agrolens.git
cd agrolens

# run setup script
chmod +x setup.sh
./setup.sh
```

The setup script will:
1. Create a Python virtual environment
2. Install all Python dependencies
3. Copy `.env.example` to `.env`
4. Download and export the ONNX model
5. Build FAISS knowledge indexes
6. Install frontend npm packages

### Configure

Add your Anthropic API key to `.env`:

```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Run

Open two terminals:

```bash
# terminal 1 — backend
source venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

```bash
# terminal 2 — frontend
cd frontend
npm run dev
```

Open `http://localhost:3000` in your browser.

---

## Demo Mode

To run without a backend (for screenshots and presentations):

```env
# in .env
DEMO_MODE=true
```

This returns hardcoded results without calling the vision model or Claude API.

---

## API

### `POST /query`

Analyze a crop image.

**Form data:**

| Field      | Type   | Required | Description                        |
|------------|--------|----------|------------------------------------|
| image      | file   | yes      | JPG, PNG or WEBP crop photo        |
| language   | string | no       | Response language (default English)|
| state      | string | no       | Indian state for scheme matching   |
| district   | string | no       | District for price data            |

**Response:**

```json
{
  "success": true,
  "crop": "Tomato",
  "disease": "Early Blight",
  "confidence": 87.4,
  "severity": "Moderate",
  "gradcam": "data:image/jpeg;base64,...",
  "treatment": [
    "Spray Mancozeb 75% WP at 2g per litre every 7–10 days",
    "Remove and burn all infected leaves immediately",
    "Switch to drip irrigation — avoid wetting leaves"
  ],
  "schemes": [
    {
      "name": "PMFBY",
      "description": "Pradhan Mantri Fasal Bima Yojana",
      "amount": "₹25,000",
      "status": "Eligible",
      "apply_url": "pmfby.gov.in",
      "documents": ["Aadhaar", "Land records", "Bank passbook"]
    }
  ],
  "language": "English",
  "latency_ms": 94
}
```

### `GET /health`

Returns `{"status": "ok"}` — use to check if backend is running.

---

## Tech Stack

| Layer       | Technology                                      |
|-------------|-------------------------------------------------|
| Vision      | EfficientNet-B0, ONNX Runtime, Grad-CAM         |
| RAG         | FAISS, sentence-transformers (all-MiniLM-L6-v2) |
| LLM         | Claude (claude-sonnet-4-6) via Anthropic API   |
| Backend     | FastAPI, Python 3.11                            |
| Frontend    | React 18, Vite, Axios                           |
| Data        | PlantVillage dataset, ICAR, TNAU, MyScheme.gov  |

---

## Dataset & Model

- **Visual classifier:** EfficientNet-B0 fine-tuned on PlantVillage (54,306 images, 14 crops, 26 diseases)
- **Disease RAG corpus:** 20 disease entries from ICAR bulletins and TNAU Agritech Portal
- **Scheme corpus:** 12 central government schemes from MyScheme.gov.in
- **Model size:** ~25 MB ONNX
- **Inference:** <100ms on CPU

> For full accuracy, fine-tune the model on PlantVillage before the demo.
> Pre-trained ImageNet weights are used by default after `scripts/download_model.py`.

---

## Differentiation

|                        | AgroLens | KissanAI | Kisan GPT |
|------------------------|----------|----------|-----------|
| Works offline          | ✓        | ✗        | ✗         |
| Photo-based diagnosis  | ✓        | ✗        | ✗         |
| Grad-CAM explainability| ✓        | ✗        | ✗         |
| 12 Indian languages    | ✓        | ✗        | ✗         |
| Scheme matching        | ✓        | partial  | ✗         |
| On-device inference    | ✓        | ✗        | ✗         |

---

## Team

Built at IEEE Hackathon 2025 — VIT Bhopal STB11518

---

## License

MIT
