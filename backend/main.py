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
    mysql_uri = os.getenv("MYSQL_URI")
    if not mysql_uri:
        print("⚠️  MYSQL_URI not configured, skipping SQL tools")
        return []
    
    try:
        db = SQLDatabase.from_uri(mysql_uri)
        toolkit = SQLDatabaseToolkit(db=db, llm=get_llm())
        print("✅ MySQL tools initialized")
        return toolkit.get_tools()
    except Exception as e:
        print(f"⚠️  MySQL connection failed, skipping SQL tools: {e}")
        return []

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
    
    tools = [mongo_tool] + mysql_tools
    
    # Update prompt based on available tools
    if not mysql_tools:
        tool_context = "You only have access to MongoDB for client data. For portfolio-related questions, explain that portfolio data is not currently available."
    else:
        tool_context = "You have access to both MongoDB (client data) and MySQL (portfolio data)."
    
    # Create agent prompt
    prompt = PromptTemplate.from_template(f"""
    You are a financial data assistant that answers questions using database tools.

    CONTEXT: {tool_context}

    CRITICAL RULES FOR TOOL USAGE:
    1. Action Input must contain ONLY the query - NO conversational text
    2. For SQL queries: provide ONLY the SQL statement
    3. For MongoDB queries: provide ONLY the search request in simple English
    4. NEVER add phrases like "Waiting for result" or "Please respond"
    5. NEVER provide Final Answer until you have tool results

    EXAMPLES:
    Good: Action Input: SELECT * FROM portfolios LIMIT 5
    Bad: Action Input: SELECT * FROM portfolios LIMIT 5; (Waiting for result...)

    Good: Action Input: Find clients from New York
    Bad: Action Input: Find clients from New York (Please let me know the output)

    FORMAT:
    Thought: I need to query [database] to find [information]
    Action: [tool_name]
    Action Input: [query_only_no_extra_text]
    Observation: [tool_result]
    Thought: Based on the results...
    Final Answer: [formatted_answer]

    Available tools: {{tools}}
    Tool names: {{tool_names}}

    Question: {{input}}

    {{agent_scratchpad}}
    """)
    
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10,
        max_execution_time=60,
        early_stopping_method="force"
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
    
    # Simple fallback for common queries to avoid agent parsing issues
    question_lower = request.question.lower()
    
    # MongoDB direct queries
    if "clients from new york" in question_lower or "new york clients" in question_lower:
        try:
            mongo_tool = get_mongo_tool()
            result = mongo_tool._run("Find clients from New York")
            
            # Format the response using ResponseFormatter
            formatter = ResponseFormatter()
            formatted_response = formatter.format_response(
                question=request.question,
                agent_output=result
            )
            
            return QueryResponse(**formatted_response)
        except Exception as e:
            print(f"Direct MongoDB query failed: {e}")
    
    # Age distribution queries
    if "age" in question_lower and ("distribution" in question_lower or "group" in question_lower):
        try:
            mongo_tool = get_mongo_tool()
            result = mongo_tool._run("Show age distribution of clients")
            
            # Format the response using ResponseFormatter
            formatter = ResponseFormatter()
            formatted_response = formatter.format_response(
                question=request.question,
                agent_output=result
            )
            
            return QueryResponse(**formatted_response)
        except Exception as e:
            print(f"Direct age distribution query failed: {e}")
    
    # SQL direct queries for portfolios
    if "top" in question_lower and ("client" in question_lower or "portfolio" in question_lower) and "equity" in question_lower:
        try:
            mysql_tools = get_mysql_tools()
            if mysql_tools:
                # Use the SQL query tool directly
                sql_tool = next((tool for tool in mysql_tools if "query" in tool.name.lower()), None)
                if sql_tool:
                    result = sql_tool._run("SELECT c.name, p.total_value FROM portfolios p JOIN clients c ON p.client_id = c.client_id ORDER BY p.total_value DESC LIMIT 5")
                    
                    # Format the response using ResponseFormatter
                    formatter = ResponseFormatter()
                    formatted_response = formatter.format_response(
                        question=request.question,
                        agent_output=result
                    )
                    
                    return QueryResponse(**formatted_response)
        except Exception as e:
            print(f"Direct SQL query failed: {e}")
    
    # SQL direct queries for best performance portfolios
    if "best performance" in question_lower or ("top" in question_lower and "performance" in question_lower):
        try:
            mysql_tools = get_mysql_tools()
            if mysql_tools:
                # Use the SQL query tool directly
                sql_tool = next((tool for tool in mysql_tools if "query" in tool.name.lower()), None)
                if sql_tool:
                    result = sql_tool._run("SELECT p.portfolio_id, p.portfolio_name, pp.cumulative_return FROM portfolios p JOIN portfolio_performance pp ON p.portfolio_id = pp.portfolio_id ORDER BY pp.cumulative_return DESC LIMIT 5")
                    
                    # Format the response using ResponseFormatter
                    formatter = ResponseFormatter()
                    formatted_response = formatter.format_response(
                        question=request.question,
                        agent_output=result
                    )
                    
                    return QueryResponse(**formatted_response)
        except Exception as e:
            print(f"Direct SQL performance query failed: {e}")
    
    try:
        # Execute the query using the agent
        result = agent_executor.invoke({"input": request.question})
        
        # Check if agent completed successfully
        if "output" not in result:
            raise HTTPException(status_code=500, detail="Agent failed to generate response")
        
        # Format the response
        formatter = ResponseFormatter()
        formatted_response = formatter.format_response(
            question=request.question,
            agent_output=result["output"]
        )
        
        return QueryResponse(**formatted_response)
        
    except ValueError as e:
        error_msg = str(e)
        if "Agent stopped due to iteration limit" in error_msg or "Invalid Format" in error_msg or "not a valid tool" in error_msg:
            return QueryResponse(
                type="text",
                data="I'm having trouble processing this query. Could you try rephrasing it more simply? For example: 'Show me clients from New York' or 'List top 5 portfolios by value'",
                metadata={"error": "agent_parsing_error", "question": request.question}
            )
        else:
            raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")
    except Exception as e:
        print(f"Query execution error: {e}")
        error_str = str(e)
        if "not a valid tool" in error_str or "Invalid Format" in error_str:
            return QueryResponse(
                type="text", 
                data="I'm having trouble understanding your request. Please try a simpler question like 'Find clients from New York' or 'Show top portfolios'",
                metadata={"error": "tool_error", "question": request.question}
            )
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