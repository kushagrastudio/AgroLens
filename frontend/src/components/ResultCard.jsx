const styles = {
  card: {
    border: "1px solid #e0e0e0",
    borderRadius: "10px",
    padding: "22px",
    marginTop: "24px",
  },
  topRow: {
    display: "flex",
    alignItems: "flex-start",
    justifyContent: "space-between",
    marginBottom: "4px",
  },
  diseaseName: {
    fontSize: "22px",
    fontWeight: "bold",
    color: "#111",
  },
  latencyBadge: {
    fontSize: "11px",
    padding: "3px 9px",
    borderRadius: "20px",
    background: "#e8f5e9",
    color: "#2e7d32",
    border: "1px solid #c8e6c9",
    whiteSpace: "nowrap",
  },
  metaRow: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    marginBottom: "18px",
  },
  cropTag: {
    fontSize: "13px",
    color: "#777",
  },
  severityBadge: (severity) => ({
    fontSize: "11px",
    fontWeight: "bold",
    padding: "2px 10px",
    borderRadius: "20px",
    background: severity === "High" ? "#fff3e0" : severity === "Moderate" ? "#fff8e1" : "#f1f8e9",
    color: severity === "High" ? "#e65100" : severity === "Moderate" ? "#f57f17" : "#558b2f",
    border: `1px solid ${severity === "High" ? "#ffcc80" : severity === "Moderate" ? "#ffe082" : "#c5e1a5"}`,
  }),
  sectionLabel: {
    fontSize: "11px",
    textTransform: "uppercase",
    letterSpacing: "0.06em",
    color: "#999",
    marginBottom: "6px",
  },
  confRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "6px",
  },
  confLabel: {
    fontSize: "13px",
    color: "#555",
  },
  confVal: {
    fontSize: "20px",
    fontWeight: "bold",
    color: "#2e7d32",
  },
  barBg: {
    height: "8px",
    background: "#e0e0e0",
    borderRadius: "4px",
    overflow: "hidden",
    marginBottom: "22px",
  },
  barFill: (confidence) => ({
    height: "100%",
    width: `${confidence}%`,
    background: confidence > 80 ? "#2e7d32" : confidence > 60 ? "#f9a825" : "#e53935",
    borderRadius: "4px",
    transition: "width 0.6s ease",
  }),
  steps: {
    display: "flex",
    flexDirection: "column",
    gap: "10px",
    marginBottom: "2px",
  },
  step: {
    display: "flex",
    alignItems: "flex-start",
    gap: "10px",
  },
  stepNum: {
    minWidth: "20px",
    height: "20px",
    background: "#2e7d32",
    color: "#fff",
    borderRadius: "50%",
    fontSize: "11px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
    marginTop: "1px",
  },
  stepText: {
    fontSize: "13px",
    color: "#555",
    lineHeight: "1.5",
  },
  divider: {
    height: "1px",
    background: "#eee",
    margin: "20px 0",
  },
  schemeCard: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "10px 12px",
    border: "1px solid #eee",
    borderRadius: "8px",
    marginBottom: "8px",
  },
  schemeName: {
    fontSize: "13px",
    fontWeight: "bold",
    color: "#222",
  },
  schemeDesc: {
    fontSize: "11px",
    color: "#999",
    marginTop: "2px",
  },
  schemeRight: {
    textAlign: "right",
  },
  schemeAmount: {
    fontSize: "13px",
    fontWeight: "bold",
    color: "#2e7d32",
  },
  schemeBadge: (status) => ({
    display: "inline-block",
    fontSize: "10px",
    padding: "1px 8px",
    borderRadius: "20px",
    marginTop: "3px",
    background: status === "Eligible" ? "#e8f5e9" : status === "Apply" ? "#e3f2fd" : "#fff8e1",
    color: status === "Eligible" ? "#2e7d32" : status === "Apply" ? "#1565c0" : "#f57f17",
    border: `1px solid ${status === "Eligible" ? "#c8e6c9" : status === "Apply" ? "#bbdefb" : "#ffe082"}`,
  }),
  applyLink: {
    display: "block",
    fontSize: "11px",
    color: "#1565c0",
    textDecoration: "none",
    marginTop: "2px",
  },
  docsSection: {
    marginTop: "20px",
  },
  docsList: {
    display: "flex",
    flexWrap: "wrap",
    gap: "6px",
    marginTop: "6px",
  },
  docTag: {
    fontSize: "11px",
    padding: "3px 10px",
    background: "#f5f5f5",
    border: "1px solid #e0e0e0",
    borderRadius: "20px",
    color: "#555",
  },
  kvkNote: {
    fontSize: "12px",
    color: "#e65100",
    background: "#fff3e0",
    border: "1px solid #ffcc80",
    borderRadius: "8px",
    padding: "10px 14px",
    marginTop: "16px",
  },
};

export default function ResultCard({ result, language }) {
  if (!result) return null;

  const {
    crop,
    disease,
    confidence,
    severity,
    treatment,
    schemes,
    latency_ms,
  } = result;

  // collect unique documents from all schemes
  const allDocs = [...new Set(
    (schemes || []).flatMap((s) => s.documents || [])
  )].slice(0, 6);

  return (
    <div style={styles.card}>

      {/* disease name + latency */}
      <div style={styles.topRow}>
        <div style={styles.diseaseName}>{disease}</div>
        {latency_ms && (
          <span style={styles.latencyBadge}>⚡ {latency_ms}ms</span>
        )}
      </div>

      {/* crop + severity */}
      <div style={styles.metaRow}>
        <span style={styles.cropTag}>
          Crop: <strong>{crop}</strong>
        </span>
        {severity && severity !== "None" && (
          <span style={styles.severityBadge(severity)}>{severity}</span>
        )}
      </div>

      {/* confidence bar */}
      <div style={styles.confRow}>
        <span style={styles.confLabel}>Confidence score</span>
        <strong style={styles.confVal}>{confidence}%</strong>
      </div>
      <div style={styles.barBg}>
        <div style={styles.barFill(confidence)} />
      </div>

      {/* treatment steps */}
      {treatment && treatment.length > 0 && (
        <>
          <p style={styles.sectionLabel}>Treatment Steps</p>
          <div style={styles.steps}>
            {treatment.map((step, i) => (
              <div key={i} style={styles.step}>
                <div style={styles.stepNum}>{i + 1}</div>
                <div style={styles.stepText}>{step}</div>
              </div>
            ))}
          </div>
        </>
      )}

      <div style={styles.divider} />

      {/* government schemes */}
      {schemes && schemes.length > 0 && (
        <>
          <p style={styles.sectionLabel}>Government Schemes</p>

          {schemes.map((scheme, i) => (
            <div key={i} style={styles.schemeCard}>
              <div>
                <div style={styles.schemeName}>{scheme.name}</div>
                <div style={styles.schemeDesc}>{scheme.description}</div>
              </div>
              <div style={styles.schemeRight}>
                <div style={styles.schemeAmount}>{scheme.amount}</div>
                <span style={styles.schemeBadge(scheme.status)}>
                  {scheme.status}
                </span>
                {scheme.apply_url && (
                  <a
                    href={`https://${scheme.apply_url}`}
                    target="_blank"
                    rel="noreferrer"
                    style={styles.applyLink}
                  >
                    Apply →
                  </a>
                )}
              </div>
            </div>
          ))}

          {/* documents needed */}
          {allDocs.length > 0 && (
            <div style={styles.docsSection}>
              <p style={styles.sectionLabel}>Documents You Will Need</p>
              <div style={styles.docsList}>
                {allDocs.map((doc, i) => (
                  <span key={i} style={styles.docTag}>{doc}</span>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* consult kvk note for low confidence */}
      {confidence < 60 && (
        <div style={styles.kvkNote}>
          ⚠️ Confidence is low. Please consult your nearest{" "}
          <strong>Krishi Vigyan Kendra (KVK)</strong> for accurate diagnosis.
        </div>
      )}

    </div>
  );
}