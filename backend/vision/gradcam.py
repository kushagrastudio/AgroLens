import numpy as np
from PIL import Image
import base64
import io
import os

# we use pytorch only for grad-cam generation
# onnx handles inference — torch is used here just for hooks
try:
    import torch
    import torch.nn as nn
    import torchvision.models as models
    import torchvision.transforms as transforms
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


# ── image preprocessing ───────────────────────────────────
def preprocess_for_torch(image_path: str):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    img = Image.open(image_path).convert("RGB")
    tensor = transform(img).unsqueeze(0)
    return tensor, img


# ── grad-cam logic ────────────────────────────────────────
class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        self._register_hooks()

    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.activations = output.detach()

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].detach()

        self.target_layer.register_forward_hook(forward_hook)
        self.target_layer.register_full_backward_hook(backward_hook)

    def generate(self, input_tensor, class_idx):
        self.model.eval()
        output = self.model(input_tensor)

        self.model.zero_grad()
        target = output[0][class_idx]
        target.backward()

        # pool gradients across channels
        pooled_grads = self.gradients.mean(dim=[0, 2, 3])

        # weight activations by pooled gradients
        activations = self.activations[0]
        for i in range(activations.shape[0]):
            activations[i] *= pooled_grads[i]

        # average across channels and relu
        heatmap = activations.mean(dim=0).numpy()
        heatmap = np.maximum(heatmap, 0)

        # normalize
        if heatmap.max() > 0:
            heatmap /= heatmap.max()

        return heatmap


# ── colorize heatmap ──────────────────────────────────────
def apply_heatmap(original_img: Image.Image, heatmap: np.ndarray) -> Image.Image:
    # resize heatmap to image size
    heatmap_img = Image.fromarray(np.uint8(255 * heatmap))
    heatmap_img = heatmap_img.resize(original_img.size, Image.BILINEAR)
    heatmap_arr = np.array(heatmap_img, dtype=np.float32) / 255.0

    # apply red-orange-yellow colormap manually
    r = np.clip(heatmap_arr * 2.0, 0, 1)
    g = np.clip(heatmap_arr * 2.0 - 1.0, 0, 1) * 0.6
    b = np.zeros_like(heatmap_arr)
    colored = np.stack([r, g, b], axis=-1)
    colored_img = Image.fromarray(np.uint8(colored * 255))

    # blend with original
    original_arr = np.array(original_img.convert("RGB"), dtype=np.float32) / 255.0
    colored_arr  = np.array(colored_img, dtype=np.float32) / 255.0
    blended = 0.55 * original_arr + 0.45 * colored_arr
    blended = np.clip(blended, 0, 1)

    return Image.fromarray(np.uint8(blended * 255))


# ── encode to base64 ──────────────────────────────────────
def image_to_base64(img: Image.Image) -> str:
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    buffer.seek(0)
    encoded = base64.b64encode(buffer.read()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


# ── main function ─────────────────────────────────────────
def generate_gradcam(image_path: str, class_idx: int) -> str | None:
    """
    Generate a Grad-CAM heatmap overlay for the given image and class.
    Returns a base64 encoded image string, or None if torch is unavailable.
    """
    if not TORCH_AVAILABLE:
        print("PyTorch not available — skipping Grad-CAM")
        return None

    try:
        # load efficientnet-b0 — same architecture as our fine-tuned model
        model = models.efficientnet_b0(weights=None)

        # replace classifier head to match our number of classes (38)
        num_classes = 38
        model.classifier[1] = nn.Linear(
            model.classifier[1].in_features,
            num_classes
        )

        # load weights if available
        weights_path = "backend/models/efficientnet_b0.pth"
        if os.path.exists(weights_path):
            model.load_state_dict(
                torch.load(weights_path, map_location="cpu")
            )

        # target the last conv layer in efficientnet-b0
        target_layer = model.features[-1][0]

        grad_cam = GradCAM(model, target_layer)

        input_tensor, original_img = preprocess_for_torch(image_path)
        input_tensor.requires_grad = True

        # clamp class idx to valid range
        class_idx = min(class_idx, num_classes - 1)

        heatmap = grad_cam.generate(input_tensor, class_idx)
        result_img = apply_heatmap(original_img, heatmap)

        return image_to_base64(result_img)

    except Exception as e:
        print(f"Grad-CAM error: {e}")
        return None