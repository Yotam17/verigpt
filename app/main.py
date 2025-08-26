#!/usr/bin/env python3
"""
VeriGPT FastAPI Service - AI-based SystemVerilog code analysis
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from openai import OpenAI
from .prompt import get_prompt

# Load environment variables
#load_dotenv()

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load embeddings (only to load FAISS, not for live embeddings)
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)
vectorstore = FAISS.load_local("data/faiss_index", embeddings, allow_dangerous_deserialization=True)

# Try to load FAISS index if it exists
try:
    faiss_path = Path("data/faiss_index")
    if faiss_path.exists():
        vectorstore = FAISS.load_local("data/faiss_index", embeddings, allow_dangerous_deserialization=True)
        print("✅ FAISS index loaded successfully")

        vec = embeddings.embed_query("fifo buffer")
        print("DEBUG: first 5 dims:", vec[:5])
        print("DEBUG: vector length:", len(vec))
    else:
        print("⚠️  FAISS index not found at data/faiss_index")
        print("   Run the agent first to create the index")
except Exception as e:
    print(f"⚠️  Could not load FAISS index: {e}")

# Import our VeriGPT agent
try:
    from .verigpt_agent import VeriGPTAgent
    agent = VeriGPTAgent()
    AGENT_READY = True
except Exception as e:
    print(f"⚠️  Warning: Could not initialize VeriGPT agent: {e}")
    agent = None
    AGENT_READY = False

app = FastAPI(
    title="VeriGPT API Service",
    description="AI-based SystemVerilog code analysis using RAG",
    version="1.0.0"
)

# Add CORS middleware to allow cross-origin requests
# ⚠️  SECURITY NOTE: This configuration allows all origins for demo purposes
#     In production, restrict allow_origins to specific domains
#     Example: allow_origins=["http://localhost:3000", "https://yourdomain.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Allow all origins (not secure for prod, but fine for demo)
    allow_credentials=True,
    allow_methods=["*"],        # Allow all HTTP methods
    allow_headers=["*"],        # Allow all headers
)

# Request models
class AnalysisRequest(BaseModel):
    """Request model for SystemVerilog analysis"""
    code: str
    model: Optional[str] = "gpt-4"
    temperature: Optional[float] = 0.1

class FileAnalysisRequest(BaseModel):
    """Request model for analyzing specific files"""
    file_paths: List[str]
    model: Optional[str] = "gpt-4"
    temperature: Optional[float] = 0.1

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str
    environment: Dict[str, Any]

class AgentRequest(BaseModel):
    """Request model for agent queries"""
    query: str
    top_k: int = 3

# Initialize VeriGPT agent


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with health information"""
    return HealthResponse(
        status="healthy" if AGENT_READY else "degraded",
        message="VeriGPT API Service is running",
        environment={
            "agent_ready": AGENT_READY,
            "openai_key_set": bool(os.getenv("OPENAI_API_KEY")),
            "data_directory": "data/raw_full"
        }
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if AGENT_READY else "degraded",
        message="Service health check",
        environment={
            "agent_ready": AGENT_READY,
            "openai_key_set": bool(os.getenv("OPENAI_API_KEY")),
            "data_directory": "data/raw_full"
        }
    )

@app.post("/analyze/code")
async def analyze_code(request: AnalysisRequest):
    """Analyze SystemVerilog code directly"""
    if not AGENT_READY:
        raise HTTPException(status_code=503, detail="VeriGPT agent not ready")
    
    try:
        # Create a temporary document for analysis
        from langchain.schema import Document
        temp_doc = Document(
            page_content=request.code,
            metadata={"source": "user_input", "filename": "user_code.sv"}
        )
        
        # Use the agent's analysis capabilities
        # For now, we'll use a simplified approach
        result = f"Analysis of SystemVerilog code:\n\n{request.code}\n\nThis is a placeholder response. Full analysis requires the complete RAG pipeline."
        
        return {
            "input": request.code,
            "analysis": result,
            "model": request.model,
            "temperature": request.temperature
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze/files")
async def analyze_files(request: FileAnalysisRequest):
    """Analyze specific SystemVerilog files"""
    if not AGENT_READY:
        raise HTTPException(status_code=503, detail="VeriGPT agent not ready")
    
    try:
        # This would require more complex file handling
        # For now, return a placeholder
        result = f"Analysis of {len(request.file_paths)} files:\n{request.file_paths}"
        
        return {
            "files": request.file_paths,
            "analysis": result,
            "model": request.model,
            "temperature": request.temperature
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File analysis failed: {str(e)}")

@app.get("/files")
async def list_files():
    """List available SystemVerilog files"""
    try:
        import glob
        
        data_dir = "data/raw_full"
        data_path = Path(data_dir)
        
        if not data_path.exists():
            return {"error": f"Data directory '{data_dir}' not found"}
        
        # Find all .sv and .svh files
        all_files = []
        for ext in ["sv", "svh"]:
            pattern = str(data_path / "**" / f"*.{ext}")
            files = glob.glob(pattern, recursive=True)
            all_files.extend(files)
        
        # Convert to relative paths
        relative_files = []
        for file_path in all_files:
            file_path_obj = Path(file_path)
            relative_path = file_path_obj.relative_to(data_path)
            relative_files.append(str(relative_path))
        
        return {
            "total_files": len(relative_files),
            "files": sorted(relative_files)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get statistics about the codebase"""
    try:
        import glob
        
        data_dir = "data/raw_full"
        data_path = Path(data_dir)
        
        if not data_path.exists():
            return {"error": f"Data directory '{data_dir}' not found"}
        
        # Count files by extension
        ext_stats = {}
        total_size = 0
        
        for ext in ["sv", "svh"]:
            pattern = str(data_path / "**" / f"*.{ext}")
            files = glob.glob(pattern, recursive=True)
            ext_stats[ext] = len(files)
            
            # Calculate total size
            for file_path in files:
                try:
                    total_size += Path(file_path).stat().st_size
                except:
                    pass
        
        return {
            "total_files": sum(ext_stats.values()),
            "file_types": ext_stats,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.get("/faiss/status")
async def get_faiss_status():
    """Get FAISS index status"""
    try:
        faiss_path = Path("data/faiss_index")
        if faiss_path.exists():
            # Count files in the index directory
            index_files = list(faiss_path.glob("*"))
            return {
                "status": "available",
                "index_path": str(faiss_path),
                "index_files": len(index_files),
                "vectorstore_loaded": vectorstore is not None
            }
        else:
            return {
                "status": "not_found",
                "index_path": str(faiss_path),
                "message": "FAISS index not found. Run the agent first to create it."
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/agent")
async def agent_endpoint(req: AgentRequest):
    """Agent endpoint for RAG-based SystemVerilog analysis"""
    if not vectorstore:
        raise HTTPException(
            status_code=503, 
            detail="FAISS index not available. Please run the agent first to create the index."
        )
    
    try:
        # Retrieve from FAISS
        docs = vectorstore.similarity_search(req.query, k=req.top_k)
        context = "\n\n".join([d.page_content for d in docs])

        print(f"Context: {context}")

        # Get system and user prompts
        system_prompt = get_prompt("agent_main_system", {})
        user_prompt = get_prompt("agent_main_user", {
            "context": context,
            "query": req.query
        })

        # Get response from the model
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )

        return {
            "answer": response.choices[0].message.content,
            "sources": [d.metadata for d in docs],
            "query": req.query,
            "top_k": req.top_k
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent query failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
