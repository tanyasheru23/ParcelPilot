from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from .metadata import DOCUMENT_METADATA

CHROMA_DIRECTORY = "data/processed/chroma"
COLLECTION_NAME = "parcelpilot_documents"

def build_vectorstore(
    pdf_directory: str,
    persist_directory: str,
):
    """
    Build the Chroma vector store from all PDFs.

    Each PDF gets its metadata from DOCUMENT_METADATA.
    That metadata is copied to every page/chunk belonging
    to that document.
    """

    pdf_directory = Path(pdf_directory)

    documents = []

    for pdf_path in pdf_directory.glob("*.pdf"):

        loader = PyPDFLoader(
            str(pdf_path)
        )

        pdf_documents = loader.load()

        metadata = DOCUMENT_METADATA.get(
            pdf_path.name,
            {}
        )

        for document in pdf_documents:

            document.metadata.update(
                {
                    "source_file": pdf_path.name,
                    **metadata,
                }
            )

        documents.extend(pdf_documents)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
    )

    chunks = splitter.split_documents(
        documents
    )

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=persist_directory,
    )

    return vectorstore

def get_vectorstore(
    persist_directory: str = CHROMA_DIRECTORY,
):
    """
    Load the existing Chroma vector store.
    """

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=persist_directory,
        embedding_function=embeddings,
    )

    return vectorstore