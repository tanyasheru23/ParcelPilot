import os
import sys

# Ensure project root is on sys.path so `src` and top-level modules import reliably
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.data.vectorstore import build_vectorstore
from config import PDF_DIRECTORY, PERSIST_DIRECTORY


if __name__ == "__main__":
    build_vectorstore(pdf_directory=PDF_DIRECTORY, persist_directory=PERSIST_DIRECTORY)
    print("Chroma vector store rebuilt successfully.")