"""
Sample data script to populate MongoDB with client information
Run this script to add sample data to your MongoDB Atlas database
"""

import os
from pymongo import MongoClient
from datetime import datetime, timedelta
import random

# MongoDB connection - will use from environment variables
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://username:password@cluster.mongodb.net/client_db?retryWrites=true&w=majority")
DATABASE_NAME = "client_db"
COLLECTION_NAME = "clients"

def generate_sample_clients():
    """Generate sample client data"""
    
    first_names = ["John", "Jane", "Michael", "Sarah", "David", "Lisa", "Robert", "Emma", "William", "Olivia", 
                   "James", "Sophia", "Alexander", "Isabella", "Benjamin", "Charlotte", "Daniel", "Amelia", 
                   "Matthew", "Mia", "Christopher", "Harper", "Andrew", "Evelyn", "Joshua", "Abigail"]
    
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", 
                  "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", 
                  "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez"]
    
    cities = [
        {"city": "New York", "state": "NY"},
        {"city": "Los Angeles", "state": "CA"},
        {"city": "Chicago", "state": "IL"},
        {"city": "Houston", "state": "TX"},
        {"city": "Phoenix", "state": "AZ"},
        {"city": "Philadelphia", "state": "PA"},
        {"city": "San Antonio", "state": "TX"},
        {"city": "San Diego", "state": "CA"},
        {"city": "Dallas", "state": "TX"},
        {"city": "San Jose", "state": "CA"},
        {"city": "Austin", "state": "TX"},
        {"city": "Jacksonville", "state": "FL"},
        {"city": "Fort Worth", "state": "TX"},
        {"city": "Columbus", "state": "OH"},
        {"city": "Charlotte", "state": "NC"},
        {"city": "San Francisco", "state": "CA"},
        {"city": "Indianapolis", "state": "IN"},
        {"city": "Seattle", "state": "WA"},
        {"city": "Denver", "state": "CO"},
        {"city": "Boston", "state": "MA"}
    ]
    
    risk_tolerances = ["low", "medium", "high"]
    sectors = ["technology", "healthcare", "finance", "energy", "real estate", "consumer goods", "utilities"]
    
    clients = []
    
    for i in range(50):  # Generate 50 sample clients
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        city_info = random.choice(cities)
        
        client = {
            "client_id": f"CLT{1000 + i}",
            "name": f"{first_name} {last_name}",
            "email": f"{first_name.lower()}.{last_name.lower()}@email.com",
            "phone": f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "age": random.randint(25, 75),
            "address": {
                "street": f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Pine', 'Elm', 'First', 'Second', 'Park', 'Washington'])} {random.choice(['St', 'Ave', 'Blvd', 'Dr', 'Ln'])}",
                "city": city_info["city"],
                "state": city_info["state"],
                "zip": f"{random.randint(10000, 99999)}"
            },
            "account_value": random.randint(10000, 5000000),
            "risk_profile": {
                "tolerance": random.choice(risk_tolerances),
                "score": random.randint(1, 10),
                "assessment_date": datetime.now() - timedelta(days=random.randint(1, 365))
            },
            "investment_preferences": {
                "preferred_sectors": random.sample(sectors, random.randint(2, 4)),
                "ESG_focused": random.choice([True, False]),
                "international_exposure": random.choice([True, False])
            },
            "created_date": datetime.now() - timedelta(days=random.randint(1, 1000)),
            "last_contact": datetime.now() - timedelta(days=random.randint(1, 90))
        }
        
        clients.append(client)
    
    return clients

def populate_mongodb():
    """Create database, collection and populate MongoDB with sample data"""
    try:
        # Connect to MongoDB Atlas
        print("🔌 Connecting to MongoDB Atlas...")
        client = MongoClient(MONGODB_URI)
        
        # Test connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas successfully")
        
        # Create/access database
        db = client[DATABASE_NAME]
        print(f"📁 Using database: {DATABASE_NAME}")
        
        # Create/access collection
        clients_collection = db[COLLECTION_NAME]
        print(f"📄 Using collection: {COLLECTION_NAME}")
        
        # Check if collection exists and has data
        existing_count = clients_collection.count_documents({})
        if existing_count > 0:
            print(f"⚠️  Found {existing_count} existing documents")
            choice = input("Do you want to replace existing data? (y/N): ").lower()
            if choice != 'y':
                print("❌ Aborted. Keeping existing data.")
                return
            
            # Clear existing data
            clients_collection.delete_many({})
            print("🗑️  Cleared existing client data")
        
        # Generate and insert sample data
        print("🔧 Generating sample client data...")
        sample_clients = generate_sample_clients()
        
        print("📥 Inserting sample clients...")
        result = clients_collection.insert_many(sample_clients)
        print(f"✅ Inserted {len(result.inserted_ids)} sample clients")
        
        # Create indexes for better query performance
        print("🔍 Creating database indexes...")
        clients_collection.create_index("client_id")
        clients_collection.create_index("name")
        clients_collection.create_index("address.city")
        clients_collection.create_index("account_value")
        clients_collection.create_index("risk_profile.tolerance")
        print("✅ Created database indexes")
        
        # Show database info
        print(f"\n📋 Database Details:")
        print(f"   Database: {DATABASE_NAME}")
        print(f"   Collection: {COLLECTION_NAME}")
        print(f"   Documents: {clients_collection.count_documents({})}")
        
        # Print sample data preview
        print("\n📊 Sample data preview:")
        for i, client in enumerate(clients_collection.find().limit(5), 1):
            print(f"{i}. {client['name']} ({client['address']['city']}, {client['address']['state']}) - ${client['account_value']:,} - Risk: {client['risk_profile']['tolerance']}")
        
        # Show available cities for testing
        cities = clients_collection.distinct("address.city")
        print(f"\n🏙️  Available cities for testing: {', '.join(cities[:10])}")
        
        client.close()
        print("\n🎉 MongoDB setup complete!")
        print("\n💡 You can now test queries like:")
        print("   - 'Find clients from New York'")
        print("   - 'Show me high-risk tolerance clients'")
        print("   - 'List clients aged between 30-50'")
        
    except Exception as e:
        print(f"❌ Error setting up MongoDB: {e}")
        print("Please check your MONGODB_URI in the .env file")

if __name__ == "__main__":
    print("🔧 MongoDB Database Setup for LangChain Financial Assistant")
    print("=" * 60)
    
    # Check if MONGODB_URI is set in environment
    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        print("❌ MONGODB_URI environment variable not found")
        print("\n📋 To set up MongoDB:")
        print("1. Make sure your backend/.env file has MONGODB_URI")
        print("2. Or set: export MONGODB_URI='your_connection_string'")
        print("3. Run this script again")
        exit(1)
    
    if mongodb_uri == "mongodb+srv://username:password@cluster.mongodb.net/client_db?retryWrites=true&w=majority":
        print("❌ MONGODB_URI is still using placeholder values")
        print("Please update it with your actual MongoDB Atlas connection string")
        exit(1)
    
    print(f"✅ Found MONGODB_URI in environment")
    print(f"🎯 Target database: {DATABASE_NAME}")
    print(f"🎯 Target collection: {COLLECTION_NAME}")
    print()
    
    # Run the setup
    populate_mongodb() 