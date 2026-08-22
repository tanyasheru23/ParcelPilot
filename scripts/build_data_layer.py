import os
import sys

# Ensure project root is on sys.path so `src` and top-level modules import reliably
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.data.sqlite_loader import load_xlsx_to_sqlite
from src.data.vectorstore import build_vectorstore

from config import XLSX_PATH, DB_PATH, PDF_DIRECTORY, PERSIST_DIRECTORY

def main():
    
    print("Building SQLite Database...")
    load_xlsx_to_sqlite(
        xlsx_path=XLSX_PATH,
        db_path=DB_PATH
    )
    print("SQLite Database created!")

    print("Building Chroma Vectorstore")
    build_vectorstore(
        pdf_directory=PDF_DIRECTORY,
        persist_directory=PERSIST_DIRECTORY
    )
    print("Chroma Vectorstore Created!")
    print("Data Layer Ready")

if __name__ == "__main__":
    main()