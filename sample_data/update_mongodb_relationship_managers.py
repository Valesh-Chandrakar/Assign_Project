"""
Script to add relationship manager data to existing MongoDB client records
Run this script to enhance your MongoDB data with relationship manager information
"""

import os
from pymongo import MongoClient
import random

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = "client_db"
COLLECTION_NAME = "clients"

def update_clients_with_relationship_managers():
    """Add relationship manager data to existing client records"""
    
    # Sample relationship managers
    relationship_managers = [
        {"name": "Sarah Johnson", "employee_id": "RM001", "specialty": "High Net Worth"},
        {"name": "Michael Chen", "employee_id": "RM002", "specialty": "Corporate Clients"},
        {"name": "Jennifer Davis", "employee_id": "RM003", "specialty": "Retirement Planning"},
        {"name": "David Rodriguez", "employee_id": "RM004", "specialty": "Investment Advisory"},
        {"name": "Lisa Thompson", "employee_id": "RM005", "specialty": "Estate Planning"},
        {"name": "Robert Wilson", "employee_id": "RM006", "specialty": "Private Banking"},
        {"name": "Emily Martinez", "employee_id": "RM007", "specialty": "Wealth Management"},
        {"name": "James Anderson", "employee_id": "RM008", "specialty": "Portfolio Management"}
    ]
    
    try:
        # Connect to MongoDB
        print("🔌 Connecting to MongoDB Atlas...")
        client = MongoClient(MONGODB_URI)
        client.admin.command('ping')
        print("✅ Connected successfully")
        
        # Access database and collection
        db = client[DATABASE_NAME]
        clients_collection = db[COLLECTION_NAME]
        
        # Get all clients
        clients = list(clients_collection.find({}))
        print(f"📋 Found {len(clients)} clients to update")
        
        if not clients:
            print("❌ No clients found in database")
            return
        
        # Update each client with a relationship manager
        updated_count = 0
        for client in clients:
            # Assign relationship manager based on account value
            account_value = client.get('account_value', 0)
            
            if account_value >= 2000000:
                # High net worth clients get specialized managers
                rm = random.choice([rm for rm in relationship_managers if rm['specialty'] in ['High Net Worth', 'Private Banking', 'Wealth Management']])
            elif account_value >= 1000000:
                # Medium wealth clients
                rm = random.choice([rm for rm in relationship_managers if rm['specialty'] in ['Investment Advisory', 'Portfolio Management', 'Estate Planning']])
            else:
                # Regular clients
                rm = random.choice([rm for rm in relationship_managers if rm['specialty'] in ['Retirement Planning', 'Corporate Clients']])
            
            # Update the client record
            update_result = clients_collection.update_one(
                {"_id": client["_id"]},
                {
                    "$set": {
                        "relationship_manager": {
                            "name": rm["name"],
                            "employee_id": rm["employee_id"],
                            "specialty": rm["specialty"],
                            "contact_email": f"{rm['name'].lower().replace(' ', '.')}@wealthmanagement.com",
                            "assigned_date": client.get('created_date', None)
                        }
                    }
                }
            )
            
            if update_result.modified_count > 0:
                updated_count += 1
        
        print(f"✅ Updated {updated_count} clients with relationship manager data")
        
        # Show sample of updated data
        print("\n📊 Sample updated clients:")
        for i, client in enumerate(clients_collection.find({}).limit(5), 1):
            rm = client.get('relationship_manager', {})
            print(f"{i}. {client['name']} -> {rm.get('name', 'N/A')} ({rm.get('specialty', 'N/A')})")
        
        # Show relationship manager distribution
        print("\n👥 Relationship Manager Distribution:")
        pipeline = [
            {"$group": {
                "_id": "$relationship_manager.name",
                "client_count": {"$sum": 1},
                "total_assets": {"$sum": "$account_value"}
            }},
            {"$sort": {"total_assets": -1}}
        ]
        
        for result in clients_collection.aggregate(pipeline):
            print(f"   {result['_id']}: {result['client_count']} clients, ${result['total_assets']:,} total assets")
        
        client.close()
        print("\n🎉 MongoDB relationship manager update complete!")
        
    except Exception as e:
        print(f"❌ Error updating MongoDB: {e}")

if __name__ == "__main__":
    print("🔧 Adding Relationship Manager Data to MongoDB")
    print("=" * 50)
    
    # Check if MONGODB_URI is set
    if not MONGODB_URI:
        print("❌ MONGODB_URI environment variable not found")
        print("Please set MONGODB_URI in your .env file")
        exit(1)
    
    # Run the update
    update_clients_with_relationship_managers() 