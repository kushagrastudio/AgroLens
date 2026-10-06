import { useState, useRef } from "react";
import axios from "axios";
import Camera from "./components/Camera";
import ResultCard from "./components/ResultCard";
import HeatmapOverlay from "./components/HeatmapOverlay";

const LANGUAGES = ["हिंदी", "English", "తెలుగు", "தமிழ்", "मराठी", "ਪੰਜਾਬੀ"];

const styles = {
  app: {
    fontFamily: "Arial, sans-serif",
    background: "#fff",
    minHeight: "100vh",
    color: "#222",
  },
  nav: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "14px 32px",
    borderBottom: "1px solid #ddd",
  },
  logo: {
    fontSize: "22px",
    fontWeight: "bold",
    color: "#2e7d32",
  },
  logoSpan: {
    color: "#111",
  },
  navLinks: {
    display: "flex",
    gap: "28px",
    listStyle: "none",
  },
  navLink: {
    textDecoration: "none",
    color: "#555",
    fontSize: "14px",
  },
  hero: {
    textAlign: "center",
    padding: "50px 20px 20px",
  },
  heroTitle: {
    fontSize: "32px",
    marginBottom: "10px",
    color: "#111",
  },
  heroSub: {
    color: "#666",
    fontSize: "15px",
    maxWidth: "480px",
    margin: "0 auto",
    lineHeight: "1.6",
  },
  container: {
    maxWidth: "600px",
    margin: "32px auto",
    padding: "0 20px",
  },
  langRow: {
    display: "flex",
    gap: "8px",
    flexWrap: "wrap",
    marginBottom: "20px",
  },
  langBtn: (active) => ({
    padding: "5px 14px",
    border: "1px solid",
    borderColor: active ? "#2e7d32" : "#ccc",
    borderRadius: "20px",
    fontSize: "13px",
    cursor: "pointer",
    background: active ? "#2e7d32" : "#fff",
    color: active ? "#fff" : "#555",
  }),
  uploadBox: {
    border: "2px dashed #bbb",
    borderRadius: "10px",
    padding: "44px 20px",
    textAlign: "center",
    cursor: "pointer",
  },
  uploadIcon: {
    fontSize: "36px",
    marginBottom: "10px",
  },
  uploadTitle: {
    display: "block",
    fontSize: "15px",
    marginBottom: "6px",
  },
  uploadSub: {
    fontSize: "13px",
    color: "#999",
    marginTop: "4px",
  },
  previewImg: {
    display: "block",
    width: "100%",
    borderRadius: "8px",
    marginTop: "14px",
    border: "1px solid #eee",
  },
  analyzeBtn: (disabled) => ({
    display: "block",
    width: "100%",
    marginTop: "16px",
    padding: "13px",
    background: disabled ? "#aaa" : "#2e7d32",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    fontSize: "15px",
    cursor: disabled ? "not-allowed" : "pointer",
  }),
  loading: {
    textAlign: "center",
    color: "#888",
    fontSize: "14px",
    padding: "18px 0",
  },
  errorBox: {
    background: "#fff3f3",
    border: "1px solid #f5c6c6",
    borderRadius: "8px",
    padding: "12px 16px",
    fontSize: "13px",
    color: "#c62828",
    marginTop: "14px",
  },
  footer: {
    textAlign: "center",
    padding: "28px 20px",
    color: "#bbb",
    fontSize: "12px",
    borderTop: "1px solid #eee",
    marginTop: "50px",
  },
};

export default function App() {
  const [lang, setLang]           = useState(1); // default English
  const [imageFile, setImageFile] = useState(null);
  const [imageURL, setImageURL]   = useState(null);
  const [loading, setLoading]     = useState(false);
  const [result, setResult]       = useState(null);
  const [error, setError]         = useState(null);
  const [showCamera, setShowCamera] = useState(false);

  const fileRef = useRef();

  // ── handle file upload ──────────────────────────────────
  function handleFile(e) {
    const file = e.target.files[0];
    if (!file) return;
    setImageFile(file);
    setImageURL(URL.createObjectURL(file));
    setResult(null);
    setError(null);
  }

  // ── handle camera capture ───────────────────────────────
  function handleCapture(file, url) {
    setImageFile(file);
    setImageURL(url);
    setShowCamera(false);
    setResult(null);
    setError(null);
  }

  // ── call backend ────────────────────────────────────────
  async function analyze() {
    if (!imageFile) return;

    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("image", imageFile);
      formData.append("language", LANGUAGES[lang]);

      const res = await axios.post(`${import.meta.env.VITE_API_URL || ""}/query`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 30000,
      });

      setResult(res.data);

    } catch (err) {
      if (err.code === "ECONNABORTED") {
        setError("Request timed out. Make sure the backend is running on port 8000.");
      } else if (err.response) {
        setError(`Server error: ${err.response.data?.detail || err.response.statusText}`);
      } else {
        setError("Cannot connect to backend. Run: uvicorn backend.main:app --reload");
      }
    } finally {
      setLoading(false);
    }
  }

  // ── reset ───────────────────────────────────────────────
  function reset() {
    setImageFile(null);
    setImageURL(null);
    setResult(null);
    setError(null);
    if (fileRef.current) fileRef.current.value = "";
  }

  return (
    <div style={styles.app}>

      {/* navbar */}
      <nav style={styles.nav}>
        <div style={styles.logo}>
          Agro<span style={styles.logoSpan}>Lens</span>
        </div>
        <ul style={styles.navLinks}>
          <li><a href="#" style={styles.navLink}>Home</a></li>
          <li><a href="#" style={styles.navLink}>About</a></li>
          <li><a href="#" style={styles.navLink}>Contact</a></li>
        </ul>
      </nav>

      {/* hero */}
      <div style={styles.hero}>
        <h1 style={styles.heroTitle}>Crop Disease Detection</h1>
        <p style={styles.heroSub}>
          Upload a photo of your crop and get instant disease diagnosis,
          treatment steps and government scheme information
        </p>
      </div>

      <div style={styles.container}>

        {/* language selector */}
        <div style={styles.langRow}>
          {LANGUAGES.map((l, i) => (
            <button
              key={i}
              style={styles.langBtn(i === lang)}
              onClick={() => setLang(i)}
            >
              {l}
            </button>
          ))}
        </div>

        {/* camera modal */}
        {showCamera && (
          <Camera
            onCapture={handleCapture}
            onClose={() => setShowCamera(false)}
          />
        )}

        {/* upload box */}
        {!imageURL && (
          <div
            style={styles.uploadBox}
            onClick={() => fileRef.current?.click()}
          >
            <div style={styles.uploadIcon}>📷</div>
            <strong style={styles.uploadTitle}>Click to upload crop image</strong>
            <p style={styles.uploadSub}>or drag and drop here</p>
            <p style={styles.uploadSub}>Supports JPG, PNG, WEBP</p>
          </div>
        )}

        <input
          type="file"
          ref={fileRef}
          accept="image/*"
          style={{ display: "none" }}
          onChange={handleFile}
        />

        {/* image preview with heatmap overlay */}
        {imageURL && (
          <HeatmapOverlay
            imageURL={imageURL}
            gradcam={result?.gradcam || null}
          />
        )}

        {/* action buttons */}
        <div style={{ display: "flex", gap: "10px", marginTop: "14px" }}>
          {!imageURL ? (
            <button
              style={{ ...styles.analyzeBtn(false), flex: 1 }}
              onClick={() => setShowCamera(true)}
            >
              📹 Use Camera
            </button>
          ) : (
            <>
              <button
                style={{ ...styles.analyzeBtn(false), flex: 1, background: "#fff", color: "#555", border: "1px solid #ccc" }}
                onClick={reset}
              >
                ✕ Clear
              </button>
              <button
                style={{ ...styles.analyzeBtn(loading || !imageFile), flex: 2 }}
                onClick={analyze}
                disabled={loading || !imageFile}
              >
                {loading ? "Analyzing..." : "Analyze Crop"}
              </button>
            </>
          )}
        </div>

        {/* loading */}
        {loading && (
          <div style={styles.loading}>
            Analyzing your crop... please wait ⏳
          </div>
        )}

        {/* error */}
        {error && (
          <div style={styles.errorBox}>
            ⚠️ {error}
          </div>
        )}

        {/* result */}
        {result && (
          <ResultCard result={result} language={LANGUAGES[lang]} />
        )}

      </div>

      <footer style={styles.footer}>
        AgroLens &copy; 2025 &nbsp;|&nbsp; IEEE Hackathon &nbsp;|&nbsp;
        Gen AI &amp; ML Track &nbsp;|&nbsp; PS 03.1
      </footer>

    </div>
  );
}