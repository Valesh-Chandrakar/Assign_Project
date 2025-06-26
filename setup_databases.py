#!/usr/bin/env python3
"""
Database Setup Script for LangChain Financial Assistant
This script sets up both MongoDB Atlas and MySQL databases with sample data.
"""

import os
import sys
from pathlib import Path

# Add backend to path to load environment variables
backend_path = Path(__file__).parent / "backend"
sys.path.append(str(backend_path))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(backend_path / ".env")

def setup_mongodb():
    """Set up MongoDB with sample client data"""
    print("🍃 Setting up MongoDB Atlas...")
    print("-" * 40)
    
    # Check if MongoDB URI is configured
    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        print("❌ MONGODB_URI not found in .env file")
        return False
    
    if "username:password" in mongodb_uri:
        print("❌ MONGODB_URI contains placeholder values")
        print("Please update backend/.env with your actual MongoDB Atlas connection string")
        return False
    
    try:
        # Import and run MongoDB setup
        sample_data_path = Path(__file__).parent / "sample_data"
        sys.path.append(str(sample_data_path))
        
        from mongodb_sample_data import populate_mongodb
        populate_mongodb()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB setup failed: {e}")
        return False

def setup_mysql():
    """Set up MySQL with portfolio data"""
    print("\n🐬 Setting up MySQL Database...")
    print("-" * 40)
    
    # Check if MySQL URI is configured
    mysql_uri = os.getenv("MYSQL_URI")
    if not mysql_uri:
        print("⚠️  MYSQL_URI not found in .env file")
        print("Skipping MySQL setup (MongoDB will work alone)")
        return True
    
    if "username:password" in mysql_uri:
        print("⚠️  MYSQL_URI contains placeholder values")
        print("Skipping MySQL setup (MongoDB will work alone)")
        return True
    
    try:
        # Import and run MySQL setup
        sample_data_path = Path(__file__).parent / "sample_data"
        sys.path.append(str(sample_data_path))
        
        from setup_mysql import main as setup_mysql_main
        return setup_mysql_main()
        
    except Exception as e:
        print(f"❌ MySQL setup failed: {e}")
        print("The application will work with MongoDB only")
        return True

def main():
    """Main setup function"""
    print("🗄️  Database Setup for LangChain + Groq Financial Assistant")
    print("=" * 65)
    
    # Check if .env file exists
    env_file = backend_path / ".env"
    if not env_file.exists():
        print("❌ No .env file found in backend directory")
        print("\n📋 Setup steps:")
        print("1. Copy backend/env_template.txt to backend/.env")
        print("2. Update .env with your actual API keys and connection strings")
        print("3. Run this script again")
        return False
    
    print("✅ Found backend/.env file")
    
    # Setup MongoDB (required)
    mongodb_success = setup_mongodb()
    if not mongodb_success:
        print("\n❌ MongoDB setup failed - this is required for the application")
        return False
    
    # Setup MySQL (optional)
    mysql_success = setup_mysql()
    
    # Summary
    print("\n" + "=" * 65)
    print("🎉 Database Setup Complete!")
    print("\n📋 Status:")
    print(f"   MongoDB Atlas: {'✅ Ready' if mongodb_success else '❌ Failed'}")
    print(f"   MySQL Database: {'✅ Ready' if mysql_success else '⚠️  Not configured'}")
    
    if mongodb_success:
        print("\n💡 You can now test queries like:")
        print("   - 'Find clients from New York'")
        print("   - 'Show me high-risk tolerance clients'")
        print("   - 'List clients aged between 30-50'")
        
        if mysql_success:
            print("   - 'Show me top 5 clients by equity value'")
            print("   - 'List recent transactions'")
    
    print("\n🚀 Next steps:")
    print("1. Start backend: cd backend && python3 main.py")
    print("2. Start frontend: cd frontend && npm run dev")
    print("3. Open http://localhost:5173 in your browser")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 