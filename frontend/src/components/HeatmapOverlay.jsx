import { useState } from "react";

const styles = {
  wrapper: {
    position: "relative",
    marginTop: "14px",
    borderRadius: "10px",
    overflow: "hidden",
    border: "1px solid #eee",
    background: "#f9f9f9",
  },
  image: {
    display: "block",
    width: "100%",
    borderRadius: "10px",
  },
  toggleRow: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "10px 12px",
    background: "#f5f5f5",
    borderTop: "1px solid #eee",
  },
  toggleLabel: {
    fontSize: "12px",
    color: "#555",
    display: "flex",
    alignItems: "center",
    gap: "8px",
  },
  switch: (on) => ({
    width: "34px",
    height: "18px",
    background: on ? "#2e7d32" : "#ccc",
    borderRadius: "9px",
    position: "relative",
    cursor: "pointer",
    transition: "background 0.2s",
    flexShrink: 0,
  }),
  knob: (on) => ({
    position: "absolute",
    top: "2px",
    left: on ? "16px" : "2px",
    width: "14px",
    height: "14px",
    background: "#fff",
    borderRadius: "50%",
    transition: "left 0.2s",
  }),
  camBadge: {
    fontSize: "11px",
    padding: "2px 9px",
    borderRadius: "20px",
    background: "rgba(239,68,68,0.12)",
    color: "#c62828",
    border: "1px solid rgba(239,68,68,0.3)",
  },
  noCamNote: {
    fontSize: "11px",
    color: "#aaa",
  },
  liveBadge: {
    position: "absolute",
    top: "10px",
    left: "10px",
    display: "flex",
    alignItems: "center",
    gap: "5px",
    background: "rgba(0,0,0,0.45)",
    padding: "3px 9px",
    borderRadius: "20px",
    fontSize: "11px",
    color: "#fff",
  },
  dot: {
    width: "6px",
    height: "6px",
    borderRadius: "50%",
    background: "#4caf50",
    flexShrink: 0,
  },
};

export default function HeatmapOverlay({ imageURL, gradcam }) {
  const [showHeatmap, setShowHeatmap] = useState(false);

  // if gradcam arrives after mount, default to showing it
  const hasGradcam = !!gradcam;

  // which image to display
  const displayURL = showHeatmap && hasGradcam ? gradcam : imageURL;

  return (
    <div style={styles.wrapper}>

      {/* image — original or heatmap */}
      <div style={{ position: "relative" }}>
        <img
          src={displayURL}
          alt={showHeatmap ? "Grad-CAM heatmap" : "uploaded crop"}
          style={styles.image}
        />

        {/* uploaded badge */}
        <div style={styles.liveBadge}>
          <div style={styles.dot} />
          {showHeatmap && hasGradcam ? "Grad-CAM" : "Uploaded"}
        </div>
      </div>

      {/* toggle bar */}
      <div style={styles.toggleRow}>
        <div style={styles.toggleLabel}>
          <div
            style={styles.switch(showHeatmap && hasGradcam)}
            onClick={() => hasGradcam && setShowHeatmap((s) => !s)}
          >
            <div style={styles.knob(showHeatmap && hasGradcam)} />
          </div>
          Show Grad-CAM heatmap
        </div>

        {hasGradcam && showHeatmap ? (
          <span style={styles.camBadge}>Attention map active</span>
        ) : !hasGradcam ? (
          <span style={styles.noCamNote}>Heatmap not available</span>
        ) : null}
      </div>

    </div>
  );
}