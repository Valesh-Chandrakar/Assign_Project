from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Union
import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.prompts import PromptTemplate

from tools.mongo_tool import MongoQueryTool
from utils.response_formatter import ResponseFormatter

load_dotenv()

app = FastAPI(title="LangChain Groq Query API", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    type: str  # "text", "table", "chart"
    data: Union[str, List[Dict], Dict]
    metadata: Dict[str, Any] = {}

# Initialize Groq LLM
def get_llm():
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable is required")
    
    return ChatGroq(
        groq_api_key=groq_api_key,
        model_name="llama3-70b-8192",  # or "mixtral-8x7b-32768"
        temperature=0.1,
        max_tokens=1000
    )

# Initialize MySQL connection
def get_mysql_tools():
    mysql_uri = os.getenv("MYSQL_URI", "mysql+pymysql://user:password@localhost/portfolio_db")
    db = SQLDatabase.from_uri(mysql_uri)
    toolkit = SQLDatabaseToolkit(db=db, llm=get_llm())
    return toolkit.get_tools()

# Initialize MongoDB tool
def get_mongo_tool():
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        raise ValueError("MONGODB_URI environment variable is required")
    
    return MongoQueryTool(connection_string=mongo_uri)

# Create the agent
def create_query_agent():
    llm = get_llm()
    
    # Get all tools
    mysql_tools = get_mysql_tools()
    mongo_tool = get_mongo_tool()
    
    tools = mysql_tools + [mongo_tool]
    
    # Create agent prompt
    prompt = PromptTemplate.from_template("""
    You are a financial data analyst assistant. You have access to two databases:
    1. MySQL database containing portfolio and transaction data
    2. MongoDB database containing client metadata and profiles
    
    When answering questions:
    - For portfolio performance, transactions, equity values: use SQL database tools
    - For client information, demographics, profiles: use MongoDB tool
    - Always format your response to indicate if it should be displayed as text, table, or chart
    - For numerical comparisons or rankings, suggest chart visualization
    - For detailed records, suggest table format
    - For summaries and explanations, use text format
    
    Available tools: {tools}
    Tool names: {tool_names}
    
    Question: {input}
    
    {agent_scratchpad}
    """)
    
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=3
    )
    
    return agent_executor

# Global agent instance
agent_executor = None

@app.on_event("startup")
async def startup_event():
    global agent_executor
    try:
        agent_executor = create_query_agent()
        print("✅ Agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        raise

@app.get("/")
async def root():
    return {"message": "LangChain Groq Query API is running!"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "groq_configured": bool(os.getenv("GROQ_API_KEY")),
        "mongodb_configured": bool(os.getenv("MONGODB_URI")),
        "mysql_configured": bool(os.getenv("MYSQL_URI"))
    }

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    if not agent_executor:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        # Execute the query using the agent
        result = agent_executor.invoke({"input": request.question})
        
        # Format the response
        formatter = ResponseFormatter()
        formatted_response = formatter.format_response(
            question=request.question,
            agent_output=result["output"]
        )
        
        return QueryResponse(**formatted_response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")

@app.get("/examples")
async def get_example_queries():
    return {
        "examples": [
            "Show me top 5 clients by equity value",
            "What are the recent transactions for high-value portfolios?",
            "List clients from New York with investment preferences",
            "Compare portfolio performance over the last quarter",
            "Show me the distribution of client age groups",
            "Which sectors have the highest returns this month?"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 