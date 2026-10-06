import os
import json
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

SCHEMES_JSON = "data/schemes.json"
INDEX_PATH   = "backend/knowledge/indexes/scheme_index"
EMBED_MODEL  = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")

_embeddings  = None
_vectorstore = None


def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBED_MODEL,
            model_kwargs={"device": "cpu"}
        )
    return _embeddings


def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        if not os.path.exists(INDEX_PATH):
            raise FileNotFoundError(
                f"Scheme index not found at {INDEX_PATH}. "
                "Run: python scripts/build_indexes.py"
            )
        _vectorstore = FAISS.load_local(
            INDEX_PATH,
            get_embeddings(),
            allow_dangerous_deserialization=True
        )
    return _vectorstore


# ── build index (called from scripts/build_indexes.py) ────
def build_scheme_index():
    if not os.path.exists(SCHEMES_JSON):
        raise FileNotFoundError(f"schemes.json not found at {SCHEMES_JSON}")

    with open(SCHEMES_JSON, "r", encoding="utf-8") as f:
        schemes = json.load(f)

    docs = []
    for scheme in schemes:
        content = f"""
Scheme: {scheme.get("name", "")}
Full Name: {scheme.get("full_name", "")}
Benefit: {scheme.get("benefit", "")}
Eligibility: {scheme.get("eligibility", "")}
Eligible Crops: {", ".join(scheme.get("eligible_crops", ["all"]))}
Eligible States: {", ".join(scheme.get("eligible_states", ["all"]))}
Documents Required: {", ".join(scheme.get("documents", []))}
Apply At: {scheme.get("apply_url", "")}
Keywords: {", ".join(scheme.get("keywords", []))}
        """.strip()

        docs.append(Document(
            page_content=content,
            metadata={
                "scheme_id": scheme.get("scheme_id", ""),
                "name":      scheme.get("name", ""),
                "amount":    scheme.get("benefit", ""),
                "apply_url": scheme.get("apply_url", "")
            }
        ))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=40
    )
    chunks = splitter.split_documents(docs)

    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    vectorstore = FAISS.from_documents(chunks, get_embeddings())
    vectorstore.save_local(INDEX_PATH)

    print(f"Scheme index built — {len(chunks)} chunks from {len(schemes)} schemes")


# ── eligibility check ──────────────────────────────────────
def check_eligibility(scheme: dict, crop: str, state: str) -> str:
    """
    Simple rule-based eligibility check.
    Returns: Eligible | Check Eligibility | Not Eligible
    """
    eligible_crops  = scheme.get("eligible_crops", ["all"])
    eligible_states = scheme.get("eligible_states", ["all"])

    crop_ok  = "all" in eligible_crops  or crop.lower()  in [c.lower() for c in eligible_crops]
    state_ok = "all" in eligible_states or state is None or state.lower() in [s.lower() for s in eligible_states]

    if crop_ok and state_ok:
        return "Eligible"
    elif crop_ok or state_ok:
        return "Check Eligibility"
    else:
        return "Not Eligible"


# ── retrieve relevant schemes ──────────────────────────────
def retrieve_schemes(crop: str, disease: str, state: str = None, k: int = 6) -> list[dict]:
    """
    Search FAISS index for schemes relevant to crop + disease + state.
    """
    query = f"{crop} {disease} farmer scheme compensation insurance"
    if state:
        query += f" {state}"

    try:
        vectorstore = get_vectorstore()
        docs = vectorstore.similarity_search_with_score(query, k=k)

        results = []
        seen = set()

        for doc, score in docs:
            name = doc.metadata.get("name", "")
            if name in seen:
                continue
            seen.add(name)
            results.append({
                "doc":   doc,
                "score": score
            })

        return results

    except Exception as e:
        print(f"Scheme retrieval error: {e}")
        return []


# ── main function ──────────────────────────────────────────
def find_schemes(
    crop: str,
    disease: str,
    state: str = None,
    language: str = "English"
) -> list[dict]:
    """
    Find and return government schemes relevant to the detected disease.
    Returns a list of scheme dicts for the frontend.
    """
    try:
        retrieved = retrieve_schemes(crop, disease, state)

        # load full scheme data to do eligibility check
        with open(SCHEMES_JSON, "r", encoding="utf-8") as f:
            all_schemes = json.load(f)

        scheme_map = {s["name"]: s for s in all_schemes}

        output = []
        for item in retrieved:
            name      = item["doc"].metadata.get("name", "")
            full_data = scheme_map.get(name, {})

            status = check_eligibility(full_data, crop, state)

            output.append({
                "name":        name,
                "description": full_data.get("full_name", name),
                "amount":      full_data.get("benefit", ""),
                "status":      status,
                "apply_url":   full_data.get("apply_url", ""),
                "documents":   full_data.get("documents", [])
            })

        # always return at least 2 results
        if not output:
            return fallback_schemes()

        return output[:4]

    except Exception as e:
        print(f"Scheme finder error: {e}")
        return fallback_schemes()


# ── hardcoded fallback ─────────────────────────────────────
def fallback_schemes() -> list[dict]:
    return [
        {
            "name":        "PMFBY",
            "description": "Pradhan Mantri Fasal Bima Yojana",
            "amount":      "₹25,000",
            "status":      "Eligible",
            "apply_url":   "pmfby.gov.in",
            "documents":   ["Aadhaar", "Land records", "Bank passbook"]
        },
        {
            "name":        "PM-KISAN",
            "description": "Direct income support for farmers",
            "amount":      "₹6,000/yr",
            "status":      "Eligible",
            "apply_url":   "pmkisan.gov.in",
            "documents":   ["Aadhaar", "Land records", "Bank account"]
        },
        {
            "name":        "Soil Health Card",
            "description": "Free soil testing and advisory",
            "amount":      "Free",
            "status":      "Apply",
            "apply_url":   "soilhealth.dac.gov.in",
            "documents":   ["Aadhaar", "Land details"]
        }
    ]