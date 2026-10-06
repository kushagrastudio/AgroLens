import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── this script does two things:
# 1. downloads pretrained efficientnet-b0 from torchvision
# 2. exports it to ONNX format for runtime inference
# note: for full accuracy, fine-tune on PlantVillage before exporting
# ─────────────────────────────────────────────────────────────────────


NUM_CLASSES = 38
MODEL_DIR   = "backend/models"
ONNX_PATH   = os.path.join(MODEL_DIR, "crop_disease.onnx")
PTH_PATH    = os.path.join(MODEL_DIR, "efficientnet_b0.pth")


def download_and_export():
    print("=" * 50)
    print("AgroLens — Model Setup")
    print("=" * 50)

    try:
        import torch
        import torch.nn as nn
        import torchvision.models as models
    except ImportError:
        print("ERROR: PyTorch not installed.")
        print("Run: pip install torch torchvision")
        sys.exit(1)

    os.makedirs(MODEL_DIR, exist_ok=True)

    # ── step 1: load efficientnet-b0 ──────────────────────
    print("\n[1/3] Loading EfficientNet-B0...")
    model = models.efficientnet_b0(
        weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1
    )

    # replace final classifier head with our 38-class head
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, NUM_CLASSES)

    model.eval()
    print(f"      Model loaded — classifier head set to {NUM_CLASSES} classes")

    # ── step 2: save pytorch weights ──────────────────────
    print("\n[2/3] Saving PyTorch weights...")
    torch.save(model.state_dict(), PTH_PATH)
    print(f"      Saved to {PTH_PATH}")
    print("      NOTE: These are ImageNet pretrained weights.")
    print("      For full accuracy, fine-tune on PlantVillage dataset.")
    print("      Fine-tuning script: python scripts/finetune.py")

    # ── step 3: export to ONNX ────────────────────────────
    print("\n[3/3] Exporting to ONNX format...")
    dummy_input = torch.randn(1, 3, 224, 224)

    torch.onnx.export(
        model,
        dummy_input,
        ONNX_PATH,
        export_params=True,
        opset_version=17,
        do_constant_folding=True,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={
            "input":  {0: "batch_size"},
            "output": {0: "batch_size"}
        }
    )
    print(f"      ONNX model saved to {ONNX_PATH}")

    # ── verify export ─────────────────────────────────────
    try:
        import onnxruntime as ort
        import numpy as np

        session = ort.InferenceSession(
            ONNX_PATH,
            providers=["CPUExecutionProvider"]
        )
        test_input = np.random.randn(1, 3, 224, 224).astype(np.float32)
        input_name = session.get_inputs()[0].name
        output = session.run(None, {input_name: test_input})

        print(f"      ONNX verified — output shape: {output[0].shape}")

    except ImportError:
        print("      onnxruntime not found — skipping verification")
    except Exception as e:
        print(f"      Verification warning: {e}")

    # ── print model info ──────────────────────────────────
    model_size_mb = os.path.getsize(ONNX_PATH) / (1024 * 1024)

    print("\n" + "=" * 50)
    print("Model setup complete")
    print(f"ONNX model size : {model_size_mb:.1f} MB")
    print(f"ONNX path       : {ONNX_PATH}")
    print(f"PyTorch path    : {PTH_PATH}")
    print(f"Input shape     : (1, 3, 224, 224)")
    print(f"Output classes  : {NUM_CLASSES}")
    print("=" * 50)
    print("\nNext step: python scripts/build_indexes.py")


def check_already_exists():
    if os.path.exists(ONNX_PATH):
        print(f"ONNX model already exists at {ONNX_PATH}")
        overwrite = input("Overwrite? (y/n): ").strip().lower()
        if overwrite != "y":
            print("Skipping download.")
            sys.exit(0)


if __name__ == "__main__":
    check_already_exists()
    download_and_export()