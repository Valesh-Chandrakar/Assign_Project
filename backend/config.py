import os

# Environment Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")
MYSQL_URI = os.getenv("MYSQL_URI")

# Example values (replace with your actual values):
# GROQ_API_KEY = "your_groq_api_key_here"
# MONGODB_URI = "mongodb+srv://username:password@cluster.mongodb.net/client_db?retryWrites=true&w=majority"
# MYSQL_URI = "mysql+pymysql://username:password@host:3306/portfolio_db" 