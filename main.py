#!/usr/bin/env python3
"""
VeriGPT FastAPI Service - AI-based SystemVerilog code analysis
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our VeriGPT agent
from verigpt_agent import VeriGPTAgent

app = FastAPI(
    title="VeriGPT API Service",
    description="AI-based SystemVerilog code analysis using RAG",
    version="1.0.0"
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

# Initialize VeriGPT agent
try:
    agent = VeriGPTAgent()
    AGENT_READY = True
except Exception as e:
    print(f"⚠️  Warning: Could not initialize VeriGPT agent: {e}")
    AGENT_READY = False

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
        from pathlib import Path
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
        from pathlib import Path
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
