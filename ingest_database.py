"""
Ingestion Script für den RAG Chatbot.

Lädt PDF Dokumente aus dem data Ordner,
zerlegt sie in Chunks und erstellt daraus Vektor-Embeddings, die in der ChromaDB gespeichert werden.    
"""

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_chroma import Chroma
from uuid import uuid4

# import the .env file
from dotenv import load_dotenv
load_dotenv()

# configuration
DATA_PATH = r"data"
CHROMA_PATH = r"chroma_db"

# initiate the embeddings model
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")

# initiate the vector store
vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings_model,
    persist_directory=CHROMA_PATH,
)

# loading the PDF document
loader = PyPDFDirectoryLoader(DATA_PATH)

raw_documents = loader.load()

# remove any documents that have no extracted text (e.g. scanned or image PDFs)
filtered_docs = [d for d in raw_documents if d.page_content and d.page_content.strip()]
skipped = len(raw_documents) - len(filtered_docs)
if skipped:
    print(f"skipped {skipped} documents with no text")

# splitting the document
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=100,
    length_function=len,
    is_separator_regex=False,
)

# creating the chunks
chunks = text_splitter.split_documents(filtered_docs)

# also filter out any empty chunks just in case
chunks = [c for c in chunks if c.page_content and c.page_content.strip()]

# creating unique ID's
uuids = [str(uuid4()) for _ in range(len(chunks))]

# adding chunks to vector store
if chunks:
    vector_store.add_documents(documents=chunks, ids=uuids)
else:
    print("no valid chunks to add to vector store")