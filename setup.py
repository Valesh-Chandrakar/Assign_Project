#!/usr/bin/env python3
"""
Quick setup script for LangChain + Groq Financial Assistant
This script helps you set up the project quickly by installing dependencies
and providing guidance for configuration.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=True, cwd=cwd, 
                              capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Check Node.js
    success, output = run_command("node --version")
    if success:
        print(f"✅ Node.js detected: {output.strip()}")
    else:
        print("❌ Node.js is required. Please install Node.js 16+")
        return False
    
    # Check npm
    success, output = run_command("npm --version")
    if success:
        print(f"✅ npm detected: {output.strip()}")
    else:
        print("❌ npm is required")
        return False
    
    return True

def setup_backend():
    """Set up the backend dependencies"""
    print("\n🔧 Setting up backend...")
    
    backend_path = Path("backend")
    if not backend_path.exists():
        print("❌ Backend directory not found")
        return False
    
    # Install Python dependencies
    print("📦 Installing Python dependencies...")
    success, output = run_command("pip3 install -r requirements.txt", cwd=backend_path)
    
    if success:
        print("✅ Backend dependencies installed successfully")
        return True
    else:
        print(f"❌ Failed to install backend dependencies: {output}")
        return False

def setup_frontend():
    """Set up the frontend dependencies"""
    print("\n🔧 Setting up frontend...")
    
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Install Node.js dependencies
    print("📦 Installing Node.js dependencies...")
    success, output = run_command("npm install", cwd=frontend_path)
    
    if success:
        print("✅ Frontend dependencies installed successfully")
        return True
    else:
        print(f"❌ Failed to install frontend dependencies: {output}")
        return False

def create_env_file():
    """Create .env file from template"""
    print("\n📝 Setting up .env file...")
    
    backend_path = Path("backend")
    env_template_path = backend_path / "env_template.txt"
    env_file_path = backend_path / ".env"
    
    if env_template_path.exists():
        try:
            # Copy template to .env file
            with open(env_template_path, "r") as template:
                content = template.read()
            
            with open(env_file_path, "w") as env_file:
                env_file.write(content)
            
            print("✅ Created backend/.env file")
            print("📝 Please edit backend/.env with your actual API keys")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("❌ Template file not found")
        return False

def main():
    """Main setup function"""
    print("🚀 LangChain + Groq Financial Assistant Setup")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed. Please install missing dependencies.")
        return False
    
    # Setup backend
    if not setup_backend():
        print("\n❌ Backend setup failed.")
        return False
    
    # Setup frontend
    if not setup_frontend():
        print("\n❌ Frontend setup failed.")
        return False
    
    # Create .env file
    create_env_file()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Get your Groq API key from https://console.groq.com/")
    print("2. Set up MongoDB Atlas at https://cloud.mongodb.com/")
    print("3. Edit backend/.env with your actual API keys")
    print("4. Run the backend: cd backend && python3 main.py")
    print("5. Run the frontend: cd frontend && npm run dev")
    print("6. Open http://localhost:5173 in your browser")
    
    return True

if __name__ == "__main__":
    main() 