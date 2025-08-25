#!/usr/bin/env python3
"""
VeriGPT Agent - AI-based SystemVerilog code analysis using RAG
"""

import os
from typing import List
from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.schema import Document
from prompt_bank import PromptBank

# Load environment variables
load_dotenv()

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
        
    def load_sv_file(self, file_path: str) -> str:
        """Load SystemVerilog file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File {file_path} not found")
        except Exception as e:
            raise Exception(f"Error reading file {file_path}: {e}")
    
    def split_content(self, content: str) -> List[Document]:
        """Split content into chunks for vectorization"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = text_splitter.split_text(content)
        return [Document(page_content=chunk, metadata={"source": "data/fifo.sv"}) for chunk in chunks]
    
    def create_vectorstore(self, documents: List[Document]) -> FAISS:
        """Create FAISS vector store from documents"""
        return FAISS.from_documents(documents, self.embeddings)
    
    def create_rag_tool(self, vectorstore: FAISS) -> Tool:
        """Create RAG retrieval tool"""
        def rag_search(query: str) -> str:
            """Search the vector store for relevant information"""
            docs = vectorstore.similarity_search(query, k=3)
            return "\n\n".join([doc.page_content for doc in docs])
        
        return Tool(
            name="SystemVerilog_Codebase_Search",
            description="Search the SystemVerilog codebase for relevant information about modules, ports, signals, and functionality",
            func=rag_search
        )
    
    def run_analysis(self, sv_file_path: str = "fifo.sv") -> str:
        """Main method to run the complete analysis"""
        print("🔍 Loading SystemVerilog file...")
        content = self.load_sv_file(sv_file_path)
        
        print("✂️  Splitting content into chunks...")
        documents = self.split_content(content)
        
        print("📚 Creating FAISS vector store...")
        vectorstore = self.create_vectorstore(documents)
        
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
        prompt = self.prompt_bank.format_prompt("analyze_sv", code_block=content)
        
        print("🚀 Running analysis...")
        result = agent.run(prompt)
        
        return result

def main():
    """Main entry point"""
    try:
        print("🚀 Starting VeriGPT Agent...")
        agent = VeriGPTAgent()
        
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

if __name__ == "__main__":
    exit(main())
