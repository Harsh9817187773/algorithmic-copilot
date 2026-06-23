# ingest.py
import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

def build_vector_db():
    print("Reading reference algorithms...")
    # Load your notes/code out of the docs folder
    loader = TextLoader("./docs/data_structures.txt")
    documents = loader.load()

    # Split text intelligently so logical blocks stay together
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=50,
        separators=["\nclass ", "\nstruct ", "\nvoid ", "\nint ", "\n\n", "\n"]
    )
    chunks = text_splitter.split_documents(documents)
    
    print(f"Split data into {len(chunks)} contextual chunks.")

    # Convert text chunks into embeddings using a free local model
    print("Generating mathematical embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Compile and save the database locally
    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local("faiss_index")
    print("Vector database built successfully and saved to 'faiss_index'!")

if __name__ == "__main__":
    build_vector_db()