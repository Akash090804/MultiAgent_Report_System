# run.py
"""
Simple script to start the AI Report Generator web server
"""

import uvicorn
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

def main():
    print("\n" + "="*60)
    print("🤖 AI REPORT GENERATOR - WEB SERVER")
    print("="*60)
    print("\n📋 Server starting...")
    print("📍 Access at: http://localhost:8000")
    print("📍 Alternative: http://127.0.0.1:8000")
    print("📍 API docs: http://localhost:8000/docs")
    print("\n⏹️  Press CTRL+C to stop\n")
    print("="*60 + "\n")
    
    # Check if frontend files exist
    if not os.path.exists("frontend/index.html"):
        print("❌ ERROR: frontend/index.html not found!")
        print("Please create the frontend files first.")
        return
    
    if not os.path.exists("frontend/app.js"):
        print("❌ ERROR: frontend/app.js not found!")
        print("Please create the frontend files first.")
        return
    
    # Check if backend files exist
    if not os.path.exists("backend/api.py"):
        print("❌ ERROR: backend/api.py not found!")
        return
    
    print("✅ All files found\n")
    print("🔗 If 'Site can't be reached' appears:")
    print("   1. Try http://127.0.0.1:8000 instead of localhost")
    print("   2. Check Windows Firewall settings")
    print("   3. Ensure port 8000 is not in use: netstat -ano | findstr :8000\n")
    
    # Run server
    uvicorn.run(
        "backend.api:app",
        host="127.0.0.1",  # Bind to loopback explicitly
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )

if __name__ == "__main__":
    main()