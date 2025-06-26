from langchain.tools import BaseTool
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, PrivateAttr
import json
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import re

class MongoQueryInput(BaseModel):
    query: str = Field(description="Natural language query to search MongoDB")

class MongoQueryTool(BaseTool):
    name: str = "mongodb_query"
    description: str = """
    Use this tool to query MongoDB for client information, demographics, and profiles.
    This tool can handle queries about:
    - Client personal information (name, age, location, contact details)
    - Investment preferences and risk profiles
    - Account metadata and settings
    - Client demographics and statistics
    
    Input should be a natural language query about client data.
    Examples:
    - "Find clients from New York"
    - "Show me high-risk tolerance clients"
    - "List clients aged between 30-50"
    - "Get client preferences for technology sector"
    """
    args_schema: type = MongoQueryInput
    
    # Use private attributes for internal state
    _connection_string: str = PrivateAttr()
    _database_name: str = PrivateAttr()
    _client: Optional[MongoClient] = PrivateAttr(default=None)
    _db: Any = PrivateAttr(default=None)
    
    def __init__(self, connection_string: str, database_name: str = "client_db", **kwargs):
        super().__init__(**kwargs)
        self._connection_string = connection_string
        self._database_name = database_name
        self._client = None
        self._db = None
        self._connect()
    
    def _connect(self):
        """Establish MongoDB connection"""
        try:
            self._client = MongoClient(self._connection_string)
            self._db = self._client[self._database_name]
            # Test connection
            self._client.admin.command('ping')
            print("✅ MongoDB connection established")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            raise
    
    def _parse_query_to_mongo(self, natural_query: str) -> Dict[str, Any]:
        """
        Convert natural language query to MongoDB query
        This is a simplified parser - in production, you might want to use a more sophisticated NLP approach
        """
        query = natural_query.lower()
        mongo_query = {}
        
        # Location-based queries
        if "from" in query and any(city in query for city in ["new york", "california", "texas", "florida"]):
            cities = ["new york", "california", "texas", "florida", "chicago", "boston", "seattle"]
            for city in cities:
                if city in query:
                    mongo_query["address.city"] = {"$regex": city, "$options": "i"}
                    break
        
        # Age-based queries
        age_pattern = r"aged?\s+(?:between\s+)?(\d+)(?:\s*-\s*(\d+))?|age\s+(\d+)"
        age_match = re.search(age_pattern, query)
        if age_match:
            if age_match.group(2):  # Range query
                min_age = int(age_match.group(1))
                max_age = int(age_match.group(2))
                mongo_query["age"] = {"$gte": min_age, "$lte": max_age}
            elif age_match.group(3):  # Specific age
                mongo_query["age"] = int(age_match.group(3))
            elif age_match.group(1):  # Single age
                mongo_query["age"] = int(age_match.group(1))
        
        # Risk tolerance queries
        if "high risk" in query or "aggressive" in query:
            mongo_query["risk_profile.tolerance"] = "high"
        elif "low risk" in query or "conservative" in query:
            mongo_query["risk_profile.tolerance"] = "low"
        elif "medium risk" in query or "moderate" in query:
            mongo_query["risk_profile.tolerance"] = "medium"
        
        # Investment preferences
        sectors = ["technology", "healthcare", "finance", "energy", "real estate", "consumer goods"]
        for sector in sectors:
            if sector in query:
                mongo_query["investment_preferences.preferred_sectors"] = {"$in": [sector]}
                break
        
        # Account value queries
        if "high value" in query or "wealthy" in query:
            mongo_query["account_value"] = {"$gte": 1000000}
        elif "low value" in query:
            mongo_query["account_value"] = {"$lte": 100000}
        
        return mongo_query
    
    def _determine_collection(self, query: str) -> str:
        """Determine which collection to query based on the query content"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["client", "customer", "profile", "demographic"]):
            return "clients"
        elif any(word in query_lower for word in ["preference", "risk", "investment"]):
            return "client_preferences"
        elif any(word in query_lower for word in ["contact", "address", "phone", "email"]):
            return "client_contacts"
        else:
            return "clients"  # Default collection
    
    def _format_results(self, results: List[Dict], query: str) -> str:
        """Format MongoDB results for display"""
        if not results:
            return "No matching records found in MongoDB."
        
        # Determine if this should be a summary or detailed view
        if len(results) > 10:
            # Summary view for large result sets
            summary = f"Found {len(results)} matching clients.\n\n"
            summary += "Sample results:\n"
            for i, doc in enumerate(results[:5]):
                summary += f"{i+1}. "
                if 'name' in doc:
                    summary += f"Name: {doc['name']}, "
                if 'age' in doc:
                    summary += f"Age: {doc['age']}, "
                if 'address' in doc and 'city' in doc['address']:
                    summary += f"City: {doc['address']['city']}, "
                if 'account_value' in doc:
                    summary += f"Account Value: ${doc['account_value']:,.2f}"
                summary += "\n"
            
            if len(results) > 5:
                summary += f"... and {len(results) - 5} more results.\n"
                
            return summary
        else:
            # Detailed view for smaller result sets
            formatted = f"Found {len(results)} matching records:\n\n"
            for i, doc in enumerate(results, 1):
                formatted += f"--- Record {i} ---\n"
                for key, value in doc.items():
                    if key != '_id':  # Skip MongoDB ObjectId
                        if isinstance(value, dict):
                            formatted += f"{key.title()}:\n"
                            for subkey, subvalue in value.items():
                                formatted += f"  {subkey.title()}: {subvalue}\n"
                        else:
                            formatted += f"{key.title()}: {value}\n"
                formatted += "\n"
            
            return formatted
    
    def _run(self, query: str) -> str:
        """Execute the MongoDB query"""
        try:
            # Determine collection and parse query
            collection_name = self._determine_collection(query)
            collection = self._db[collection_name]
            
            # Convert natural language to MongoDB query
            mongo_query = self._parse_query_to_mongo(query)
            
            # If no specific query was parsed, do a general search
            if not mongo_query:
                # Try to extract keywords for text search
                keywords = re.findall(r'\b[a-zA-Z]+\b', query)
                if keywords:
                    # Use text search if available, otherwise search in common fields
                    mongo_query = {
                        "$or": [
                            {"name": {"$regex": "|".join(keywords), "$options": "i"}},
                            {"address.city": {"$regex": "|".join(keywords), "$options": "i"}},
                            {"investment_preferences.preferred_sectors": {"$in": keywords}}
                        ]
                    }
            
            # Execute query with limit to prevent overwhelming responses
            results = list(collection.find(mongo_query).limit(20))
            
            # Format and return results
            formatted_results = self._format_results(results, query)
            
            return formatted_results
            
        except PyMongoError as e:
            return f"MongoDB query error: {str(e)}"
        except Exception as e:
            return f"Error processing query: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Async version of _run"""
        return self._run(query)
    
    def __del__(self):
        """Close MongoDB connection when tool is destroyed"""
        if hasattr(self, '_client') and self._client:
            self._client.close() 