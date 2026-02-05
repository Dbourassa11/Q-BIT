#!/usr/bin/env python3
"""
SGPA API Quick Start Script

Starts the Sacred Geometric Principles of Alignment API server.
"""

import uvicorn

if __name__ == "__main__":
    print("🔮 Starting Sacred Geometric Principles of Alignment API...")
    print("📊 Dashboard: http://localhost:8000/dashboard")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🌟 May your systems align with the cosmos! 🌟\n")

    uvicorn.run(
        "src.api.sgpa_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
