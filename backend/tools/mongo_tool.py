from langchain.tools import BaseTool
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
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
    
    def __init__(self, connection_string: str, database_name: str = "client_db", **kwargs):
        super().__init__(**kwargs)
        # Store connection details as instance variables (not Pydantic fields)
        object.__setattr__(self, 'connection_string', connection_string)
        object.__setattr__(self, 'database_name', database_name)
        object.__setattr__(self, 'client', None)
        object.__setattr__(self, 'db', None)
        self._connect()
    
    def _connect(self):
        """Establish MongoDB connection"""
        try:
            # Close existing connection if any
            if hasattr(self, 'client') and self.client:
                self.client.close()
            
            client = MongoClient(self.connection_string)
            db = client[self.database_name]
            # Test connection
            client.admin.command('ping')
            object.__setattr__(self, 'client', client)
            object.__setattr__(self, 'db', db)
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
    
    def _handle_aggregation_query(self, query: str) -> Optional[List[Dict]]:
        """Handle aggregation queries like grouping by relationship manager"""
        query_lower = query.lower()
        
        # Relationship manager aggregation (breakdown/grouping)
        if "relationship manager" in query_lower and ("group" in query_lower or "breakdown" in query_lower or "portfolio" in query_lower):
            pipeline = [
                {
                    "$match": {
                        "relationship_manager": {"$exists": True}
                    }
                },
                {
                    "$group": {
                        "_id": "$relationship_manager.name",
                        "client_count": {"$sum": 1},
                        "total_portfolio_value": {"$sum": "$account_value"},
                        "avg_portfolio_value": {"$avg": "$account_value"},
                        "manager_specialty": {"$first": "$relationship_manager.specialty"}
                    }
                },
                {
                    "$sort": {"total_portfolio_value": -1}
                },
                {
                    "$project": {
                        "relationship_manager": "$_id",
                        "client_count": 1,
                        "total_portfolio_value": 1,
                        "avg_portfolio_value": 1,
                        "manager_specialty": 1,
                        "_id": 0
                    }
                }
            ]
            
            try:
                collection = self.db["clients"]
                results = list(collection.aggregate(pipeline))
                return results
            except Exception as e:
                print(f"Aggregation query failed: {e}")
                return None
        
        # Top relationship managers
        if "top" in query_lower and "relationship manager" in query_lower:
            pipeline = [
                {
                    "$match": {
                        "relationship_manager": {"$exists": True}
                    }
                },
                {
                    "$group": {
                        "_id": "$relationship_manager.name",
                        "client_count": {"$sum": 1},
                        "total_portfolio_value": {"$sum": "$account_value"},
                        "avg_portfolio_value": {"$avg": "$account_value"},
                        "manager_specialty": {"$first": "$relationship_manager.specialty"},
                        "manager_employee_id": {"$first": "$relationship_manager.employee_id"}
                    }
                },
                {
                    "$sort": {"total_portfolio_value": -1}
                },
                {
                    "$limit": 10
                },
                {
                    "$project": {
                        "relationship_manager": "$_id",
                        "client_count": 1,
                        "total_portfolio_value": 1,
                        "avg_portfolio_value": 1,
                        "manager_specialty": 1,
                        "manager_employee_id": 1,
                        "_id": 0
                    }
                }
            ]
            
            try:
                collection = self.db["clients"]
                results = list(collection.aggregate(pipeline))
                return results
            except Exception as e:
                print(f"Top relationship managers query failed: {e}")
                return None
        
        return None
    
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
            # Ensure connection is active
            if not hasattr(self, 'client') or not self.client:
                self._connect()
            
            # Test connection and reconnect if needed
            try:
                self.client.admin.command('ping')
            except:
                print("🔄 MongoDB connection lost, reconnecting...")
                self._connect()
            
            # Check if this is an aggregation query first
            aggregation_results = self._handle_aggregation_query(query)
            if aggregation_results is not None:
                return self._format_aggregation_results(aggregation_results, query)
            
            # Determine collection and parse query
            collection_name = self._determine_collection(query)
            collection = self.db[collection_name]
            
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
    
    def _format_aggregation_results(self, results: List[Dict], query: str) -> str:
        """Format aggregation results for display"""
        if not results:
            return "No matching records found in MongoDB."
        
        query_lower = query.lower()
        
        if "top" in query_lower and "relationship manager" in query_lower:
            formatted = f"Top Relationship Managers by Portfolio Value:\n\n"
            
            for i, result in enumerate(results, 1):
                formatted += f"--- Rank {i} ---\n"
                formatted += f"Name: {result.get('relationship_manager', 'N/A')}\n"
                formatted += f"Employee ID: {result.get('manager_employee_id', 'N/A')}\n"
                formatted += f"Specialty: {result.get('manager_specialty', 'N/A')}\n"
                formatted += f"Client Count: {result.get('client_count', 0)}\n"
                formatted += f"Total Portfolio Value: ${result.get('total_portfolio_value', 0):,.2f}\n"
                formatted += f"Average Portfolio Value: ${result.get('avg_portfolio_value', 0):,.2f}\n"
                formatted += "\n"
        else:
            # Regular breakdown format
            formatted = f"Portfolio Value Breakdown by Relationship Manager:\n\n"
            
            for i, result in enumerate(results, 1):
                formatted += f"--- Manager {i} ---\n"
                formatted += f"Name: {result.get('relationship_manager', 'N/A')}\n"
                formatted += f"Specialty: {result.get('manager_specialty', 'N/A')}\n"
                formatted += f"Client Count: {result.get('client_count', 0)}\n"
                formatted += f"Total Portfolio Value: ${result.get('total_portfolio_value', 0):,.2f}\n"
                formatted += f"Average Portfolio Value: ${result.get('avg_portfolio_value', 0):,.2f}\n"
                formatted += "\n"
        
        return formatted
    
    async def _arun(self, query: str) -> str:
        """Async version of _run"""
        return self._run(query)
    
    def close_connection(self):
        """Manually close MongoDB connection if needed"""
        if hasattr(self, 'client') and self.client:
            self.client.close()
            object.__setattr__(self, 'client', None)
            object.__setattr__(self, 'db', None) 