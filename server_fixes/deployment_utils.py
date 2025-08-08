"""
Server Deployment Fixes for Healthcare AI System
"""

import os
from pathlib import Path

def check_environment():
    """Check if running in production environment"""
    return os.getenv('ENVIRONMENT', 'development') == 'production'

def get_websocket_url():
    """Get appropriate WebSocket URL based on environment"""
    if check_environment():
        # Production: Use environment variable or default
        host = os.getenv('SERVER_HOST', 'your-server.com')
        return f"wss://{host}/ws"
    else:
        # Development
        return "ws://localhost:8000/ws"

def update_cors_settings(app):
    """Update CORS settings for production"""
    from fastapi.middleware.cors import CORSMiddleware
    
    if check_environment():
        # Production: Restrict origins
        origins = [
            os.getenv('FRONTEND_URL', 'https://your-server.com'),
            "https://localhost:3000",  # For local testing
        ]
    else:
        # Development: Allow all
        origins = ["*"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def configure_static_files(app):
    """Configure static file serving"""
    from fastapi.staticfiles import StaticFiles
    
    static_path = Path("static")
    if static_path.exists():
        app.mount("/static", StaticFiles(directory="static"), name="static")
    else:
        print("⚠️  Warning: static directory not found")

def check_ollama_connection():
    """Check if Ollama is available"""
    import requests
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is available")
            return True
    except:
        pass
    
    print("⚠️  Ollama not available - AI features may be limited")
    return False

def verify_file_permissions():
    """Verify file permissions for uploads directory"""
    upload_dir = Path("uploads")
    
    if not upload_dir.exists():
        upload_dir.mkdir(exist_ok=True)
        print("✅ Created uploads directory")
    
    # Test write permissions
    try:
        test_file = upload_dir / "test.txt"
        test_file.write_text("test")
        test_file.unlink()
        print("✅ Upload directory is writable")
    except Exception as e:
        print(f"❌ Upload directory permission error: {e}")
        print("   Fix: chmod 755 uploads")

def check_required_models():
    """Check if required AI models are loaded"""
    try:
        from healthcare_ai_complete_all_fixes import ai_models
        
        if ai_models.xray_model:
            print("✅ X-ray AI model loaded")
        else:
            print("⚠️  X-ray model not loaded")
            
        if ai_models.ocr_reader:
            print("✅ OCR model loaded")
        else:
            print("⚠️  OCR model not loaded")
    except Exception as e:
        print(f"⚠️  AI models not available: {e}")

# Server startup checks
if __name__ == "__main__":
    print("\n🔍 Running server deployment checks...\n")
    
    print("1. Environment Check:")
    env = "Production" if check_environment() else "Development"
    print(f"   Running in {env} mode")
    
    print("\n2. File Permissions:")
    verify_file_permissions()
    
    print("\n3. Ollama Connection:")
    check_ollama_connection()
    
    print("\n4. AI Models:")
    check_required_models()
    
    print("\n✅ Deployment checks complete!")
