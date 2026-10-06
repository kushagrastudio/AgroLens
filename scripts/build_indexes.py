import sys
import os

# add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.knowledge.treatment_rag import build_disease_index
from backend.knowledge.scheme_finder import build_scheme_index


def main():
    print("=" * 50)
    print("AgroLens — Building Knowledge Indexes")
    print("=" * 50)

    # build disease index
    print("\n[1/2] Building disease index...")
    try:
        build_disease_index()
        print("      Disease index built successfully")
    except FileNotFoundError as e:
        print(f"      ERROR: {e}")
        print("      Make sure data/diseases.json exists")
        sys.exit(1)
    except Exception as e:
        print(f"      ERROR building disease index: {e}")
        sys.exit(1)

    # build scheme index
    print("\n[2/2] Building scheme index...")
    try:
        build_scheme_index()
        print("      Scheme index built successfully")
    except FileNotFoundError as e:
        print(f"      ERROR: {e}")
        print("      Make sure data/schemes.json exists")
        sys.exit(1)
    except Exception as e:
        print(f"      ERROR building scheme index: {e}")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("All indexes built successfully")
    print("Indexes saved to: backend/knowledge/indexes/")
    print("=" * 50)


if __name__ == "__main__":
    main()