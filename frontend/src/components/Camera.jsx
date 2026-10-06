import { useRef, useEffect, useState } from "react";

const styles = {
  overlay: {
    position: "fixed",
    top: 0,
    left: 0,
    width: "100%",
    height: "100%",
    background: "rgba(0,0,0,0.85)",
    zIndex: 1000,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  modal: {
    background: "#fff",
    borderRadius: "12px",
    padding: "20px",
    width: "90%",
    maxWidth: "480px",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "14px",
  },
  title: {
    fontSize: "16px",
    fontWeight: "bold",
    color: "#111",
  },
  closeBtn: {
    background: "none",
    border: "none",
    fontSize: "20px",
    cursor: "pointer",
    color: "#888",
  },
  video: {
    width: "100%",
    borderRadius: "8px",
    background: "#000",
  },
  canvas: {
    display: "none",
  },
  btnRow: {
    display: "flex",
    gap: "10px",
    marginTop: "14px",
  },
  captureBtn: {
    flex: 1,
    padding: "12px",
    background: "#2e7d32",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    fontSize: "14px",
    cursor: "pointer",
  },
  switchBtn: {
    padding: "12px 16px",
    background: "#fff",
    color: "#555",
    border: "1px solid #ccc",
    borderRadius: "8px",
    fontSize: "14px",
    cursor: "pointer",
  },
  errorText: {
    color: "#c62828",
    fontSize: "13px",
    textAlign: "center",
    padding: "20px 0",
  },
  previewImg: {
    width: "100%",
    borderRadius: "8px",
    marginBottom: "10px",
  },
  retakeBtn: {
    flex: 1,
    padding: "12px",
    background: "#fff",
    color: "#555",
    border: "1px solid #ccc",
    borderRadius: "8px",
    fontSize: "14px",
    cursor: "pointer",
  },
  useBtn: {
    flex: 1,
    padding: "12px",
    background: "#2e7d32",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    fontSize: "14px",
    cursor: "pointer",
  },
};

export default function Camera({ onCapture, onClose }) {
  const videoRef  = useRef();
  const canvasRef = useRef();

  const [stream, setStream]       = useState(null);
  const [error, setError]         = useState(null);
  const [facingMode, setFacingMode] = useState("environment"); // rear camera
  const [captured, setCaptured]   = useState(null); // base64 preview after capture

  // ── start camera ────────────────────────────────────────
  useEffect(() => {
    startCamera();
    return () => stopCamera();
  }, [facingMode]);

  async function startCamera() {
    stopCamera();
    setError(null);

    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode, width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      });

      setStream(mediaStream);

      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        videoRef.current.play();
      }

    } catch (err) {
      if (err.name === "NotAllowedError") {
        setError("Camera permission denied. Please allow camera access in your browser settings.");
      } else if (err.name === "NotFoundError") {
        setError("No camera found on this device.");
      } else {
        setError(`Camera error: ${err.message}`);
      }
    }
  }

  function stopCamera() {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      setStream(null);
    }
  }

  // ── capture photo from video frame ──────────────────────
  function capture() {
    const video  = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;

    canvas.width  = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const dataURL = canvas.toDataURL("image/jpeg", 0.92);
    setCaptured(dataURL);
    stopCamera();
  }

  // ── retake — restart camera ──────────────────────────────
  function retake() {
    setCaptured(null);
    startCamera();
  }

  // ── use captured photo ───────────────────────────────────
  function usePhoto() {
    if (!captured) return;

    // convert base64 to File object
    const byteString = atob(captured.split(",")[1]);
    const mimeType   = "image/jpeg";
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
    }
    const blob = new Blob([ab], { type: mimeType });
    const file = new File([blob], "capture.jpg", { type: mimeType });

    onCapture(file, captured);
  }

  // ── switch front/rear camera ─────────────────────────────
  function switchCamera() {
    setCaptured(null);
    setFacingMode((prev) => (prev === "environment" ? "user" : "environment"));
  }

  return (
    <div style={styles.overlay} onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div style={styles.modal}>

        {/* header */}
        <div style={styles.header}>
          <span style={styles.title}>📷 Take a Photo</span>
          <button style={styles.closeBtn} onClick={onClose}>✕</button>
        </div>

        {/* error state */}
        {error && (
          <div style={styles.errorText}>{error}</div>
        )}

        {/* captured preview */}
        {captured && !error && (
          <>
            <img src={captured} alt="captured" style={styles.previewImg} />
            <div style={styles.btnRow}>
              <button style={styles.retakeBtn} onClick={retake}>
                🔄 Retake
              </button>
              <button style={styles.useBtn} onClick={usePhoto}>
                ✓ Use this photo
              </button>
            </div>
          </>
        )}

        {/* live video */}
        {!captured && !error && (
          <>
            <video
              ref={videoRef}
              style={styles.video}
              autoPlay
              playsInline
              muted
            />
            <div style={styles.btnRow}>
              <button style={styles.switchBtn} onClick={switchCamera}>
                🔁 Flip
              </button>
              <button style={styles.captureBtn} onClick={capture}>
                📸 Capture
              </button>
            </div>
          </>
        )}

        <canvas ref={canvasRef} style={styles.canvas} />

      </div>
    </div>
  );
}