from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from dotenv import load_dotenv
from pathlib import Path
import glob, os, sys

def build_index(data_dir="data/raw_full", out_dir="data/faiss_index"):
    print("🚀 Building FAISS index...")

    # טען .env אם קיים (נוח לפיתוח מקומי)
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY is not set. Export it or put it in .env", file=sys.stderr)
        sys.exit(1)

    files = glob.glob(str(Path(data_dir) / "**/*.sv"), recursive=True) \
          + glob.glob(str(Path(data_dir) / "**/*.svh"), recursive=True)

    documents = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            content = fh.read()
            documents.append(Document(page_content=content, metadata={"source": f}))

    print(f"📄 Loaded {len(documents)} documents")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)
    print(f"✂️ Split into {len(chunks)} chunks")

    # ✅ OpenAIEmbeddings מהחבילה langchain-openai
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=api_key
    )

    vectorstore = FAISS.from_documents(chunks, embeddings)

    Path(out_dir).mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(out_dir)
    print(f"✅ Saved FAISS index to {out_dir}")

if __name__ == "__main__":
    build_index()
