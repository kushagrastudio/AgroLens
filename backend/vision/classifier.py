import onnxruntime as ort
import numpy as np
from PIL import Image
import time
import os
from dotenv import load_dotenv

load_dotenv()

MODEL_PATH = os.getenv("ONNX_MODEL_PATH", "backend/models/crop_disease.onnx")

# disease classes from PlantVillage dataset
CLASSES = [
    {"crop": "Apple",       "disease": "Apple Scab",               "severity": "High"},
    {"crop": "Apple",       "disease": "Black Rot",                "severity": "High"},
    {"crop": "Apple",       "disease": "Cedar Apple Rust",         "severity": "Moderate"},
    {"crop": "Apple",       "disease": "Healthy",                  "severity": "None"},
    {"crop": "Blueberry",   "disease": "Healthy",                  "severity": "None"},
    {"crop": "Cherry",      "disease": "Powdery Mildew",           "severity": "Moderate"},
    {"crop": "Cherry",      "disease": "Healthy",                  "severity": "None"},
    {"crop": "Corn",        "disease": "Cercospora Leaf Spot",     "severity": "Moderate"},
    {"crop": "Corn",        "disease": "Common Rust",              "severity": "High"},
    {"crop": "Corn",        "disease": "Northern Leaf Blight",     "severity": "High"},
    {"crop": "Corn",        "disease": "Healthy",                  "severity": "None"},
    {"crop": "Grape",       "disease": "Black Rot",                "severity": "High"},
    {"crop": "Grape",       "disease": "Esca (Black Measles)",     "severity": "High"},
    {"crop": "Grape",       "disease": "Leaf Blight",              "severity": "Moderate"},
    {"crop": "Grape",       "disease": "Healthy",                  "severity": "None"},
    {"crop": "Orange",      "disease": "Citrus Greening",          "severity": "High"},
    {"crop": "Peach",       "disease": "Bacterial Spot",           "severity": "Moderate"},
    {"crop": "Peach",       "disease": "Healthy",                  "severity": "None"},
    {"crop": "Pepper",      "disease": "Bacterial Spot",           "severity": "Moderate"},
    {"crop": "Pepper",      "disease": "Healthy",                  "severity": "None"},
    {"crop": "Potato",      "disease": "Early Blight",             "severity": "Moderate"},
    {"crop": "Potato",      "disease": "Late Blight",              "severity": "High"},
    {"crop": "Potato",      "disease": "Healthy",                  "severity": "None"},
    {"crop": "Raspberry",   "disease": "Healthy",                  "severity": "None"},
    {"crop": "Soybean",     "disease": "Healthy",                  "severity": "None"},
    {"crop": "Squash",      "disease": "Powdery Mildew",           "severity": "Moderate"},
    {"crop": "Strawberry",  "disease": "Leaf Scorch",              "severity": "Moderate"},
    {"crop": "Strawberry",  "disease": "Healthy",                  "severity": "None"},
    {"crop": "Tomato",      "disease": "Bacterial Spot",           "severity": "Moderate"},
    {"crop": "Tomato",      "disease": "Early Blight",             "severity": "Moderate"},
    {"crop": "Tomato",      "disease": "Late Blight",              "severity": "High"},
    {"crop": "Tomato",      "disease": "Leaf Mold",                "severity": "Moderate"},
    {"crop": "Tomato",      "disease": "Septoria Leaf Spot",       "severity": "Moderate"},
    {"crop": "Tomato",      "disease": "Spider Mites",             "severity": "Low"},
    {"crop": "Tomato",      "disease": "Target Spot",              "severity": "Moderate"},
    {"crop": "Tomato",      "disease": "Yellow Leaf Curl Virus",   "severity": "High"},
    {"crop": "Tomato",      "disease": "Mosaic Virus",             "severity": "High"},
    {"crop": "Tomato",      "disease": "Healthy",                  "severity": "None"},
]

# load ONNX session once at startup
_session = None

def get_session():
    global _session
    if _session is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"ONNX model not found at {MODEL_PATH}. "
                "Run: python scripts/download_model.py"
            )
        _session = ort.InferenceSession(
            MODEL_PATH,
            providers=["CPUExecutionProvider"]
        )
    return _session


def preprocess(image_path: str) -> np.ndarray:
    """
    Resize and normalize image for EfficientNet-B0
    Input size: 224x224
    Normalization: ImageNet mean/std
    """
    img = Image.open(image_path).convert("RGB")
    img = img.resize((224, 224))

    arr = np.array(img, dtype=np.float32) / 255.0

    # imagenet normalization
    mean = np.array([0.485, 0.456, 0.406])
    std  = np.array([0.229, 0.224, 0.225])
    arr = (arr - mean) / std

    # HWC -> NCHW
    arr = arr.transpose(2, 0, 1)
    arr = np.expand_dims(arr, axis=0)

    return arr.astype(np.float32)


def classify_image(image_path: str) -> dict:
    """
    Run inference on a crop image.
    Returns crop name, disease, confidence, severity, class index.
    """
    session = get_session()

    start = time.time()
    input_tensor = preprocess(image_path)

    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: input_tensor})
    latency_ms = round((time.time() - start) * 1000, 1)

    # softmax
    logits = outputs[0][0]
    exp_logits = np.exp(logits - np.max(logits))
    probs = exp_logits / exp_logits.sum()

    class_idx = int(np.argmax(probs))
    confidence = round(float(probs[class_idx]) * 100, 1)

    # clamp class index to available classes
    class_idx = min(class_idx, len(CLASSES) - 1)
    label = CLASSES[class_idx]

    return {
        "crop":       label["crop"],
        "disease":    label["disease"],
        "severity":   label["severity"],
        "confidence": confidence,
        "class_idx":  class_idx,
        "latency_ms": latency_ms
    }