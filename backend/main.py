from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import shutil
import uuid
import os
from dotenv import load_dotenv

from backend.vision.classifier import classify_image
from backend.vision.gradcam import generate_gradcam
from backend.knowledge.treatment_rag import get_treatment
from backend.knowledge.scheme_finder import find_schemes

load_dotenv()

app = FastAPI(title="AgroLens API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
UPLOAD_DIR = "/tmp/agrolens"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ── health check ──────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "AgroLens is running", "demo_mode": DEMO_MODE}


@app.get("/health")
def health():
    return {"status": "ok"}


# ── main query endpoint ───────────────────────────────────
@app.post("/query")
async def query(
    image: UploadFile = File(None),
    text: str = Form(None),
    language: str = Form("English"),
    state: str = Form(None),
    district: str = Form(None),
):
    # demo mode — return hardcoded data for testing
    if DEMO_MODE:
        return demo_response()

    if image is None:
        raise HTTPException(status_code=400, detail="Image is required")

    # save uploaded image
    ext = image.filename.split(".")[-1]
    image_path = f"{UPLOAD_DIR}/{uuid.uuid4()}.{ext}"
    with open(image_path, "wb") as f:
        shutil.copyfileobj(image.file, f)

    try:
        # step 1 — run vision model
        vision_result = classify_image(image_path)

        # step 2 — generate grad-cam heatmap
        gradcam_base64 = generate_gradcam(image_path, vision_result["class_idx"])

        # step 3 — get treatment from RAG
        treatment = get_treatment(
            disease=vision_result["disease"],
            crop=vision_result["crop"],
            language=language
        )

        # step 4 — find matching schemes
        schemes = find_schemes(
            crop=vision_result["crop"],
            disease=vision_result["disease"],
            state=state,
            language=language
        )

        return {
            "success": True,
            "crop": vision_result["crop"],
            "disease": vision_result["disease"],
            "confidence": vision_result["confidence"],
            "severity": vision_result["severity"],
            "gradcam": gradcam_base64,
            "treatment": treatment,
            "schemes": schemes,
            "language": language,
            "latency_ms": vision_result.get("latency_ms")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # clean up uploaded file
        if os.path.exists(image_path):
            os.remove(image_path)


# ── demo fallback ─────────────────────────────────────────
def demo_response():
    return {
        "success": True,
        "crop": "Tomato",
        "disease": "Early Blight",
        "confidence": 87.4,
        "severity": "Moderate",
        "gradcam": None,
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
                "status": "Eligible"
            },
            {
                "name": "PM-KISAN",
                "description": "Direct income support",
                "amount": "₹6,000/yr",
                "status": "Eligible"
            },
            {
                "name": "Soil Health Card",
                "description": "Free soil testing and advisory",
                "amount": "Free",
                "status": "Apply"
            }
        ],
        "language": "English",
        "latency_ms": 94
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)