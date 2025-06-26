# 🧠 LangChain + Groq Financial Assistant

A modern financial data assistant that uses **LangChain** with **Groq AI** to provide natural language querying of client and portfolio data. The system intelligently routes queries between MongoDB (client data) and MySQL (portfolio data) and returns results as text, tables, or charts.

## 🏗️ Architecture

```
Frontend (React + Vite)
    ↓ HTTP API calls
Backend (FastAPI + LangChain + Groq)
    ↓ Intelligent routing
MongoDB Atlas (Client Data) + MySQL (Portfolio Data)
```

## 🧱 Tech Stack

| Layer          | Technology                | Purpose                                |
| -------------- | ------------------------- | -------------------------------------- |
| **Frontend**   | React 18 + Vite          | Modern UI with hot reload              |
|                | Material-UI (MUI)         | Professional component library         |
|                | Chart.js + react-chartjs-2| Interactive data visualizations        |
|                | Axios                     | API communication                      |
| **Backend**    | FastAPI                   | High-performance Python API server    |
|                | LangChain                 | AI agent orchestration framework      |
|                | **Groq API**              | Ultra-fast LLM inference              |
| **Databases**  | MongoDB Atlas             | Client metadata and profiles          |
|                | MySQL                     | Portfolio and transaction data         |
| **AI/ML**      | Groq LLaMA 3 / Mixtral   | Natural language understanding        |

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB Atlas account
- MySQL database (optional for full demo)
- Groq API key

### 1. Clone and Setup

```bash
git clone <your-repo>
cd langchain-groq-financial-assistant
```

### 2. Backend Setup

```bash
cd backend

# Install Python dependencies
pip3 install -r requirements.txt

# Copy environment template and edit with your keys
cp env_template.txt .env
# Edit .env file with your actual API keys

# Run the backend
python3 main.py
```

The backend will start on `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install Node.js dependencies
npm install

# Start development server
npm run dev
```

The frontend will start on `http://localhost:5173`

### 4. Add Sample Data (Optional)

```bash
cd sample_data

# Update the MongoDB URI in the script
# Then run:
python3 mongodb_sample_data.py
```

## 🔑 Getting Your API Keys

### Groq API Key
1. Visit [Groq Console](https://console.groq.com/)
2. Sign up/login
3. Go to API Keys section
4. Create a new API key
5. Copy the key and set it as `GROQ_API_KEY`

### MongoDB Atlas
1. Visit [MongoDB Atlas](https://cloud.mongodb.com/)
2. Create a free cluster
3. Get your connection string
4. Replace username/password in the URI
5. Set it as `MONGODB_URI`

## 📖 API Documentation

### Backend Endpoints

- `GET /` - Health check
- `GET /health` - System status (Groq, MongoDB, MySQL)
- `POST /ask` - Main query endpoint
- `GET /examples` - Sample query examples

### Query Examples

Try these natural language queries:

```
"Show me top 5 clients by equity value"
"List clients from New York with investment preferences"
"What are the recent transactions for high-value portfolios?"
"Compare portfolio performance over the last quarter"
"Show me the distribution of client age groups"
"Which sectors have the highest returns this month?"
```

## 🎯 How It Works

### 1. Query Processing Flow

```mermaid
graph TD
    A[User enters natural language query] --> B[Frontend sends to /ask endpoint]
    B --> C[LangChain agent powered by Groq LLM]
    C --> D{Determine data source}
    D -->|Client info| E[MongoDB Query Tool]
    D -->|Portfolio data| F[SQL Database Tool]
    E --> G[Response Formatter]
    F --> G
    G --> H{Response Type}
    H -->|Text| I[Text Display]
    H -->|Tabular| J[Data Table]
    H -->|Numerical| K[Interactive Chart]
```

### 2. Intelligent Data Routing

The LangChain agent automatically determines whether to query:

- **MongoDB**: For client demographics, risk profiles, contact info
- **MySQL**: For portfolio values, transactions, performance data

### 3. Response Formatting

Results are automatically formatted as:

- **📝 Text**: Explanations, summaries, insights
- **📊 Tables**: Detailed records, client lists
- **📈 Charts**: Performance comparisons, distributions

## 🛠️ Development

### Project Structure

```
langchain-groq-financial-assistant/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── tools/
│   │   └── mongo_tool.py       # Custom MongoDB LangChain tool
│   │   └── sql_tool.py         # Custom SQL LangChain tool
│   ├── utils/
│   │   └── response_formatter.py # Response formatting logic
│   ├── config.py               # Configuration management
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── App.jsx            # Main application
│   │   └── main.jsx           # Entry point
│   ├── package.json           # Node.js dependencies
│   └── vite.config.js         # Vite configuration
├── sample_data/
│   └── mongodb_sample_data.py  # Sample data generator
└── README.md                   # This file
```

### Adding New Query Types

1. **Extend MongoDB Tool**: Add new query patterns in `mongo_tool.py`
2. **Extend SQL Tool**: Add new query patterns in `sql_tool.py`
3. **Update Response Formatter**: Add new formatting logic in `response_formatter.py`
4. **Frontend Components**: Extend chart/table components for new data types

### Environment Variables

Create a `.env` file in the `backend/` directory with these variables:

```bash
# Required
GROQ_API_KEY=your_groq_api_key
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/client_db

# Optional  
MYSQL_URI=mysql+pymysql://username:password@host:3306/portfolio_db
DEBUG=True
ENVIRONMENT=development
```

You can use the provided template:
```bash
cd backend
cp env_template.txt .env
# Then edit .env with your actual values
```

## 🚀 Deployment

### Backend Deployment (Railway/Render/GCP)

```bash
# Build requirements
pip freeze > requirements.txt

# Set environment variables in your hosting platform
# Deploy using your platform's CLI or web interface
```

### Frontend Deployment (Vercel/Netlify)

```bash
npm run build
# Deploy the `dist/` folder to your hosting platform
```

## 🧪 Testing

### Backend Testing

```bash
cd backend

# Test health endpoint
curl http://localhost:8000/health

# Test query endpoint
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Show me top 5 clients by equity value"}'
```

### Frontend Testing

```bash
cd frontend
npm run dev
# Open http://localhost:5173 and test the interface
```

## 🎯 Features

### ✅ Implemented
- [x] Natural language query interface
- [x] Groq LLM integration via LangChain
- [x] MongoDB Atlas connectivity
- [x] Intelligent response formatting (text/table/chart)
- [x] React frontend with Material-UI
- [x] Interactive charts with Chart.js
- [x] Health monitoring and status indicators
- [x] Example queries and help system

### 🔄 Roadmap
- [ ] MySQL integration for portfolio data
- [ ] User authentication and sessions
- [ ] Query history and favorites
- [ ] Export functionality (PDF, Excel)
- [ ] Advanced chart types and customization
- [ ] Real-time data updates
- [ ] Mobile app version

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter issues:

1. Check the health endpoint: `http://localhost:8000/health`
2. Verify your environment variables are set correctly
3. Check MongoDB Atlas connection and whitelist your IP
4. Ensure Groq API key is valid and has credits
5. Review the console logs for error messages

## 🙏 Acknowledgments

- [LangChain](https://langchain.com/) for the AI orchestration framework
- [Groq](https://groq.com/) for ultra-fast LLM inference
- [MongoDB Atlas](https://mongodb.com/atlas) for managed MongoDB hosting
- [FastAPI](https://fastapi.tiangolo.com/) for the high-performance Python API
- [Material-UI](https://mui.com/) for the React component library

---

**Built with ❤️ using LangChain, Groq AI, and modern web technologies** 