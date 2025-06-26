"""
Sample data script to populate MongoDB with client information
Run this script to add sample data to your MongoDB Atlas database
"""

import os
from pymongo import MongoClient
from datetime import datetime, timedelta
import random

# MongoDB connection - replace with your actual connection string
MONGODB_URI = "mongodb+srv://username:password@cluster.mongodb.net/client_db?retryWrites=true&w=majority"
DATABASE_NAME = "client_db"

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
    """Populate MongoDB with sample data"""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        
        # Test connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas")
        
        # Generate and insert sample data
        clients_collection = db.clients
        
        # Clear existing data (optional)
        clients_collection.delete_many({})
        print("🗑️  Cleared existing client data")
        
        # Insert sample clients
        sample_clients = generate_sample_clients()
        result = clients_collection.insert_many(sample_clients)
        
        print(f"✅ Inserted {len(result.inserted_ids)} sample clients")
        
        # Create indexes for better query performance
        clients_collection.create_index("client_id")
        clients_collection.create_index("name")
        clients_collection.create_index("address.city")
        clients_collection.create_index("account_value")
        clients_collection.create_index("risk_profile.tolerance")
        
        print("✅ Created database indexes")
        
        # Print some sample data
        print("\n📊 Sample data preview:")
        for client in clients_collection.find().limit(3):
            print(f"- {client['name']} ({client['address']['city']}, {client['address']['state']}) - ${client['account_value']:,}")
        
        client.close()
        print("\n🎉 Sample data setup complete!")
        
    except Exception as e:
        print(f"❌ Error setting up sample data: {e}")

if __name__ == "__main__":
    print("🔧 Setting up MongoDB sample data...")
    print("📝 Make sure to update MONGODB_URI with your actual connection string")
    
    # Auto-run if MONGODB_URI is set in environment
    mongodb_uri = os.getenv("MONGODB_URI")
    if mongodb_uri and mongodb_uri != "mongodb+srv://username:password@cluster.mongodb.net/client_db?retryWrites=true&w=majority":
        populate_mongodb()
    else:
        print("\n⚠️  To run this script:")
        print("1. Set MONGODB_URI environment variable with your connection string")
        print("2. Or uncomment the populate_mongodb() call and update MONGODB_URI")
        print("3. Run: python3 mongodb_sample_data.py") 