#!/usr/bin/env python3
"""
Script to run the FastAPI server for FlashThreat.
"""

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("Starting FlashThreat Backend Server...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
