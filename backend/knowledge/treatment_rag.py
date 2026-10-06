import os
import json
import re
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from groq import Groq

load_dotenv()

DISEASES_JSON = "data/diseases.json"
INDEX_PATH    = "backend/knowledge/indexes/disease_index"
EMBED_MODEL   = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
GROQ_MODEL    = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# load once at startup
_embeddings  = None
_vectorstore = None
_client      = None


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
                f"Disease index not found at {INDEX_PATH}. "
                "Run: python scripts/build_indexes.py"
            )
        _vectorstore = FAISS.load_local(
            INDEX_PATH,
            get_embeddings(),
            allow_dangerous_deserialization=True
        )
    return _vectorstore


def get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client


# ── build index (called from scripts/build_indexes.py) ───
def build_disease_index():
    if not os.path.exists(DISEASES_JSON):
        raise FileNotFoundError(f"diseases.json not found at {DISEASES_JSON}")

    with open(DISEASES_JSON, "r") as f:
        diseases = json.load(f)

    docs = []
    for entry in diseases:
        content = f"""
Crop: {entry.get("crop", "")}
Disease: {entry.get("disease", "")}
Symptoms: {entry.get("symptoms", "")}
Cause: {entry.get("cause", "")}
Treatment: {" | ".join(entry.get("treatment", []))}
Prevention: {entry.get("prevention", "")}
Affected States: {", ".join(entry.get("states_affected", []))}
Season Risk: {", ".join(entry.get("season_risk", []))}
        """.strip()

        docs.append(Document(
            page_content=content,
            metadata={
                "id":      entry.get("id", ""),
                "crop":    entry.get("crop", ""),
                "disease": entry.get("disease", "")
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

    print(f"Disease index built — {len(chunks)} chunks from {len(diseases)} entries")


# ── retrieve relevant context ─────────────────────────────
def retrieve_disease_context(disease: str, crop: str, k: int = 4) -> str:
    query = f"{crop} {disease} symptoms treatment"
    vectorstore = get_vectorstore()
    docs = vectorstore.similarity_search(query, k=k)
    return "\n\n".join([d.page_content for d in docs])


# ── system prompt ─────────────────────────────────────────
TREATMENT_SYSTEM_PROMPT = """You are an expert plant pathologist with deep knowledge
of Indian crop diseases and ICAR/TNAU treatment guidelines.

Given the detected disease and retrieved information, provide:
1. A one-line summary of the disease
2. Exactly 3 treatment steps — practical, with product names and doses
3. One prevention tip for next season

Rules:
- Keep each step under 15 words
- Use doses farmers can measure easily (grams per litre, not kg/ha)
- If confidence is low, recommend consulting the local KVK
- Respond in the language requested

Return ONLY a JSON object in this exact format with no extra text:
{
  "summary": "one line description",
  "treatment": ["step 1", "step 2", "step 3"],
  "prevention": "one prevention tip",
  "consult_kvk": true or false
}"""


# ── main function ─────────────────────────────────────────
def get_treatment(disease: str, crop: str, language: str = "English") -> list[str]:
    """
    Retrieve treatment steps for a detected disease using RAG + Groq.
    Returns a list of treatment step strings.
    """
    # get context from FAISS
    try:
        context = retrieve_disease_context(disease, crop)
    except Exception:
        context = f"Disease: {disease}, Crop: {crop}"

    prompt = f"""
Detected disease: {disease}
Crop: {crop}
Language for response: {language}

Retrieved disease information:
{context}

Provide treatment steps following the format in your instructions.
    """.strip()

    try:
        client = get_client()

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            max_tokens=500,
            messages=[
                {"role": "system", "content": TREATMENT_SYSTEM_PROMPT},
                {"role": "user",   "content": prompt}
            ]
        )

        raw = response.choices[0].message.content.strip()

        # parse JSON response
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data.get("treatment", fallback_treatment(disease))

    except Exception as e:
        print(f"Treatment RAG error: {e}")

    return fallback_treatment(disease)


# ── hardcoded fallback ────────────────────────────────────
def fallback_treatment(disease: str) -> list[str]:
    fallbacks = {
        "Early Blight": [
            "Spray Mancozeb 75% WP at 2g per litre every 7–10 days",
            "Remove and burn all infected leaves immediately",
            "Switch to drip irrigation — avoid wetting leaves"
        ],
        "Late Blight": [
            "Spray Metalaxyl + Mancozeb at 2.5g per litre immediately",
            "Remove infected plants from field and destroy",
            "Avoid overhead irrigation and improve field drainage"
        ],
        "Bacterial Spot": [
            "Spray Copper Oxychloride 50% WP at 3g per litre",
            "Remove and destroy infected leaves and fruit",
            "Avoid working in field when plants are wet"
        ]
    }
    return fallbacks.get(disease, [
        "Consult your local Krishi Vigyan Kendra (KVK) for treatment",
        "Remove visibly infected plant parts immediately",
        "Avoid overhead irrigation and ensure good air circulation"
    ])