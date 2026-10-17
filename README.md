# 🌾 AgroLens

<div align="center">

<img width="120" src="https://cdn-icons-png.flaticon.com/512/628/628324.png" />

## 🚜 Offline-capable crop disease detection for Indian smallholder farmers.

### Upload a photo, get disease diagnosis, treatment steps, and government scheme information — no internet required for inference.

<img src="https://img.shields.io/badge/Open%20Source-GSSoC-orange?style=for-the-badge" />
<img src="https://img.shields.io/badge/AI-Powered-success?style=for-the-badge" />
<img src="https://img.shields.io/badge/React-Frontend-blue?style=for-the-badge" />
<img src="https://img.shields.io/badge/Node.js-Backend-green?style=for-the-badge" />
<img src="https://img.shields.io/badge/Made%20for-Bharat-orange?style=for-the-badge" />

</div>

---

# 📌 Overview


* 📱 **On-Device Detection** — EfficientNet-B0 (ONNX)
* 🎯 **Visual Explainability** — Grad-CAM Heatmaps
* 📚 **Offline Local RAG** — FAISS + ICAR / TNAU Guidelines

---

# ✨ Features

* **On-Device Disease Detection:** Identifies crop diseases instantly from a photo using an optimized EfficientNet-B0 model (ONNX format) running entirely local on the device.
* **Explainable AI (Grad-CAM):** Generates visual Grad-CAM heatmaps to highlight the exact regions of the leaf the model analyzed, building trust through transparency.
* **Guideline-Backed RAG Treatment:** Retrieves contextual treatment and management steps powered by an offline FAISS vector database indexed with official ICAR and TNAU agricultural guidelines.
* **Government Scheme Integration:** Automatically maps diagnosed crop issues to eligible Indian agricultural schemes (e.g., PMFBY, PM-KISAN, State Relief Funds).
* **Multilingual Support:** Fully accessible across 12 Indian regional languages to empower diverse farming communities.
* **Offline-First Architecture:** Core detection, heatmap generation, and treatment retrieval work completely offline — internet connectivity is required only for optional Claude API enhancements.


# 🛠 Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Vision** | EfficientNet-B0, ONNX Runtime, Grad-CAM |
| **RAG** | FAISS, sentence-transformers (`all-MiniLM-L6-v2`) |
| **LLM** | Claude 3.5 Sonnet via Anthropic API |
| **Backend** | FastAPI, Python 3.11 |
| **Frontend** | React 18, Vite, Axios |
| **Data Sources** | PlantVillage dataset, ICAR, TNAU, MyScheme.gov |
---

## 📊 Dataset & Model

| Feature | Details |
| :--- | :--- |
| **Visual Classifier** | EfficientNet-B0 fine-tuned on PlantVillage (54,306 images across 14 crops & 26 diseases) |
| **Disease RAG Corpus** | 20 curated disease entries sourced from official ICAR bulletins & TNAU Agritech Portal |
| **Scheme Corpus** | 12 Central Government agricultural welfare schemes from MyScheme.gov.in |
| **Model Footprint** | ~25 MB ONNX format (optimized for edge execution) |
| **Inference Speed** | <100ms on CPU |

> 💡 **Tip:** For optimal accuracy during evaluation/demo, fine-tune the model on the PlantVillage dataset. Running `scripts/download_model.py` loads default pre-trained ImageNet weights.

---

# 📁 Project Structure

```text
agrolens/
├── backend/
│   ├── main.py               # FastAPI entry point
│   ├── vision/
│   │   ├── classifier.py     # EfficientNet-B0 ONNX inference
│   │   └── gradcam.py        # Grad-CAM heatmap generation
│   ├── knowledge/
│   │   ├── treatment_rag.py  # FAISS RAG for disease treatment
│   │   ├── scheme_finder.py  # Government scheme retrieval
│   │   └── indexes/          # Built FAISS indexes (auto-generated)
│   └── models/               # ONNX model files (auto-downloaded)
├── data/
│   ├── diseases.json         # Disease corpus (20 entries)
│   └── schemes.json          # Government schemes (12 entries)
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Main React app
│   │   └── components/
│   │       ├── Camera.jsx         # Live camera capture
│   │       ├── ResultCard.jsx     # Disease result display
│   │       └── HeatmapOverlay.jsx # Grad-CAM toggle overlay
│   ├── index.html
│   └── package.json
├── scripts/
│   ├── download_model.py     # Downloads and exports ONNX model
│   └── build_indexes.py      # Builds FAISS indexes from JSON data
├── .env.example
├── requirements.txt
└── setup.sh

---

### ⚡ Differentiation Matrix

| Feature | AgroLens 🌿 | KissanAI | Kisan GPT |
| :--- | :---: | :---: | :---: |
| **Works Offline**             | ✅ | ❌ | ❌ |
| **Photo-Based Diagnosis**     | ✅ | ❌ | ❌ |
| **Grad-CAM Explainability**   | ✅ | ❌ | ❌ |
| **12 Indian Languages**       | ✅ | ❌ | ❌ |
| **Government Scheme Matching**| ✅ | ⚠️ Partial | ❌ |
| **On-Device Edge Inference**  | ✅ | ❌ | ❌ |

---

## 2️⃣ Install Dependencies

### Frontend

```bash
cd frontend
npm install
```

### Backend

```bash
cd backend
npm install
```


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

Add your GROQ API key to `.env`:

```env
GROQ_API_KEY=sk-ant-your-key-here
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
---

### `GET /health`

Returns `{"status": "ok"}` — use to check if backend is running.

---


# 💖 Support the Project

If you like this project:

⭐ Star the repository  
🍴 Fork the project  
🐛 Raise issues  
🚀 Contribute to the project  

---
---
