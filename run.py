"""
Main FastAPI application entry point for Crypto-UPI Backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import the app from the new API structure
from src.api.main import app

# Keep the existing run configuration for backward compatibility
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "run:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 