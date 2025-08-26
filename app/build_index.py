from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import glob, os
from pathlib import Path

def build_index(data_dir="data/raw_full", out_dir="data/faiss_index"):
    print("🚀 Building FAISS index...")

    # אסוף קבצי SystemVerilog
    files = glob.glob(str(Path(data_dir) / "**/*.sv"), recursive=True) \
          + glob.glob(str(Path(data_dir) / "**/*.svh"), recursive=True)

    documents = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            content = fh.read()
            documents.append(Document(page_content=content, metadata={"source": f}))

    print(f"📄 Loaded {len(documents)} documents")

    # חלק לצ'אנקים
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)
    print(f"✂️ Split into {len(chunks)} chunks")

    # צור embeddings + FAISS
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)

    # שמירה
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(out_dir)
    print(f"✅ Saved FAISS index to {out_dir}")

if __name__ == "__main__":
    build_index()
