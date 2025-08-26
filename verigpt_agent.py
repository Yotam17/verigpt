#!/usr/bin/env python3
"""
VeriGPT Agent - AI-based SystemVerilog code analysis using RAG
"""

import os
import glob
from typing import List
from pathlib import Path
from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import Document
from prompt_bank import PromptBank

# Debug: Check if environment variables are loaded
def debug_env_vars():
    """Debug function to check environment variables"""
    print("🔍 Debug: Environment variables check:")
    print(f"  OPENAI_API_KEY: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not set'}")
    print(f"  OPENAI_MODEL: {os.getenv('OPENAI_MODEL', 'Not set')}")
    print(f"  OPENAI_TEMPERATURE: {os.getenv('OPENAI_TEMPERATURE', 'Not set')}")
    
    # Check if .env file exists
    env_file = Path('.env')
    if env_file.exists():
        print(f"  .env file: ✅ Found at {env_file.absolute()}")
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
                print(f"  .env variables: {len(lines)} variables found")
        except Exception as e:
            print(f"  .env read error: {e}")
    else:
        print(f"  .env file: ❌ Not found")

# Allowed file extensions
ALLOWED_FILE_EXTENSIONS = ["sv", "svh"]

class VeriGPTAgent:
    """Main agent class for SystemVerilog code analysis"""
    
    def __init__(self):
        """Initialize the agent with OpenAI API key"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            openai_api_key=self.api_key
        )
        self.embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)
        self.prompt_bank = PromptBank()
        
    def load_sv_files_from_data(self, data_dir: str = "data/raw_full") -> List[Document]:
        """Load all SystemVerilog files from data/raw_full directory recursively"""
        documents = []
        data_path = Path(data_dir)
        
        if not data_path.exists():
            raise FileNotFoundError(f"Data directory '{data_dir}' not found")
        
        # Find all files with allowed extensions recursively
        all_files = []
        for ext in ALLOWED_FILE_EXTENSIONS:
            pattern = str(data_path / "**" / f"*.{ext}")
            files = glob.glob(pattern, recursive=True)
            all_files.extend(files)
        
        if not all_files:
            raise FileNotFoundError(f"No files with extensions {ALLOWED_FILE_EXTENSIONS} found in {data_dir}")
        
        print(f"🔍 Found {len(all_files)} files with extensions {ALLOWED_FILE_EXTENSIONS}:")
        
        for file_path in all_files:
            try:
                file_path_obj = Path(file_path)
                # Calculate relative path from data/raw_full
                relative_path = file_path_obj.relative_to(data_path)
                
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                    # Create document with comprehensive metadata
                    doc = Document(
                        page_content=content,
                        metadata={
                            "filename": file_path_obj.name,
                            "path": str(relative_path),
                            "full_path": str(file_path_obj),
                            "extension": file_path_obj.suffix,
                            "size": len(content)
                        }
                    )
                    documents.append(doc)
                    print(f"  ✅ Loaded: {relative_path} ({len(content)} chars)")
                    
            except Exception as e:
                print(f"  ❌ Error reading {file_path}: {e}")
        
        return documents
    
    def split_content(self, documents: List[Document]) -> List[Document]:
        """Split content into chunks for vectorization"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        
        all_chunks = []
        
        for doc in documents:
            chunks = text_splitter.split_text(doc.page_content)
            # Preserve metadata for each chunk
            for i, chunk in enumerate(chunks):
                chunk_doc = Document(
                    page_content=chunk,
                    metadata={
                        **doc.metadata,
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }
                )
                all_chunks.append(chunk_doc)
        
        print(f"✂️  Split into {len(all_chunks)} chunks from {len(documents)} files")
        return all_chunks
    
    def create_vectorstore(self, documents: List[Document]) -> FAISS:
        """Create FAISS vector store from documents"""
        return FAISS.from_documents(documents, self.embeddings)
    
    def create_rag_tool(self, vectorstore: FAISS) -> Tool:
        """Create RAG retrieval tool"""
        def rag_search(query: str) -> str:
            """Search the vector store for relevant information"""
            docs = vectorstore.similarity_search(query, k=5)  # Increased to 5 for better coverage
            results = []
            for doc in docs:
                filename = doc.metadata.get("filename", "unknown")
                path = doc.metadata.get("path", "unknown")
                chunk_info = f"[chunk {doc.metadata.get('chunk_index', 0)+1}/{doc.metadata.get('total_chunks', 1)}]"
                results.append(f"--- From {path} {chunk_info} ---\n{doc.page_content}")
            return "\n\n".join(results)
        
        return Tool(
            name="SystemVerilog_Codebase_Search",
            description="Search the SystemVerilog codebase for relevant information about modules, ports, signals, and functionality. Returns content from multiple files with source information.",
            func=rag_search
        )
    
    def run_analysis(self, data_dir: str = "data/raw_full") -> str:
        """Main method to run the complete analysis"""
        print("🔍 Loading SystemVerilog files from data/raw_full directory...")
        documents = self.load_sv_files_from_data(data_dir)
        
        print("✂️  Splitting content into chunks...")
        chunked_documents = self.split_content(documents)
        
        print("📚 Creating FAISS vector store...")
        vectorstore = self.create_vectorstore(chunked_documents)
        
        print("🛠️  Setting up RAG tool...")
        rag_tool = self.create_rag_tool(vectorstore)
        
        print("🤖 Initializing agent...")
        agent = initialize_agent(
            tools=[rag_tool],
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True
        )
        
        print("📝 Loading analysis prompt...")
        # Create a summary of all loaded files for the prompt
        file_summary = "\n\n".join([
            f"File: {doc.metadata['path']}\nSize: {doc.metadata['size']} chars\nPreview:\n{doc.page_content[:500]}..."
            for doc in documents[:3]  # Show first 3 files as preview
        ])
        
        prompt = self.prompt_bank.format_prompt("analyze_sv", code_block=file_summary)
        
        print("🚀 Running analysis...")
        result = agent.run(prompt)
        
        return result

    def test_file_loading(self, data_dir: str = "data/raw_full") -> None:
        """Test function to check file loading without running the full analysis"""
        print("🧪 Testing file loading...")
        try:
            documents = self.load_sv_files_from_data(data_dir)
            print(f"✅ Successfully loaded {len(documents)} files")
            
            # Show some statistics
            total_size = sum(doc.metadata.get("size", 0) for doc in documents)
            print(f"📊 Total content size: {total_size:,} characters")
            
            # Show file distribution by directory
            dir_stats = {}
            for doc in documents:
                path_parts = Path(doc.metadata["path"]).parts
                if len(path_parts) > 1:
                    top_dir = path_parts[0]
                    dir_stats[top_dir] = dir_stats.get(top_dir, 0) + 1
            
            print("📁 Files by top-level directory:")
            for dir_name, count in sorted(dir_stats.items()):
                print(f"  {dir_name}/: {count} files")
            
            # Show metadata example for first file
            if documents:
                first_doc = documents[0]
                print(f"\n📋 Metadata example for first file:")
                for key, value in first_doc.metadata.items():
                    print(f"  {key}: {value}")
                
        except Exception as e:
            print(f"❌ Error in test: {e}")

def main():
    """Main entry point"""
    try:
        print("🚀 Starting VeriGPT Agent...")
        
        # Debug environment variables first
        debug_env_vars()
        print()
        
        agent = VeriGPTAgent()
        
        # Test file loading first
        agent.test_file_loading()
        
        print("\n" + "="*50)
        print("🚀 Starting full analysis...")
        print("="*50)
        
        result = agent.run_analysis()
        
        print("\n" + "="*50)
        print("📊 ANALYSIS RESULTS")
        print("="*50)
        print(result)
        print("="*50)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

def test_structure_only():
    """Test function to check file structure without OpenAI dependencies"""
    print("🧪 Testing file structure only...")
    
    try:
        from pathlib import Path
        import glob
        
        data_dir = "data/raw_full"
        data_path = Path(data_dir)
        
        if not data_path.exists():
            print(f"❌ Data directory '{data_dir}' not found")
            return False
        
        # Find all .sv and .svh files
        all_files = []
        for ext in ["sv", "svh"]:
            pattern = str(data_path / "**" / f"*.{ext}")
            files = glob.glob(pattern, recursive=True)
            all_files.extend(files)
        
        print(f"🔍 Found {len(all_files)} SystemVerilog files:")
        
        # Group by directory
        dir_stats = {}
        for file_path in all_files:
            file_path_obj = Path(file_path)
            relative_path = file_path_obj.relative_to(data_path)
            top_dir = relative_path.parts[0] if relative_path.parts else "root"
            dir_stats[top_dir] = dir_stats.get(top_dir, 0) + 1
            print(f"  ✅ {relative_path}")
        
        print(f"\n📁 Files by top-level directory:")
        for dir_name, count in sorted(dir_stats.items()):
            print(f"  {dir_name}/: {count} files")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_env_only():
    """Test function to check environment variables without OpenAI dependencies"""
    print("🧪 Testing environment variables only...")
    debug_env_vars()
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test-structure":
            exit(0 if test_structure_only() else 1)
        elif sys.argv[1] == "--test-env":
            exit(0 if test_env_only() else 1)
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Available options: --test-structure, --test-env")
            exit(1)
    else:
        exit(main())
