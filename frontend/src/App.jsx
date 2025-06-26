import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Paper,
  ThemeProvider,
  createTheme,
  CssBaseline
} from '@mui/material';
import QueryInput from './components/QueryInput';
import ResultDisplay from './components/ResultDisplay';
import ExampleQueries from './components/ExampleQueries';
import HealthStatus from './components/HealthStatus';
import './App.css';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    h3: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 500,
    },
  },
});

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleQuery = async (question) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
      console.error('Query error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (exampleQuery) => {
    handleQuery(exampleQuery);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ mb: 4, textAlign: 'center' }}>
          <Typography variant="h3" component="h1" gutterBottom color="primary">
            🧠 LangChain + Groq Financial Assistant
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
            Ask questions about your clients and portfolios in natural language
          </Typography>
          <HealthStatus />
        </Box>

        <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
          <QueryInput 
            onSubmit={handleQuery} 
            loading={loading} 
          />
        </Paper>

        {(result || error || loading) && (
          <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
            <ResultDisplay 
              result={result}
              loading={loading}
              error={error}
            />
          </Paper>
        )}

        <Paper elevation={1} sx={{ p: 3 }}>
          <ExampleQueries onExampleClick={handleExampleClick} />
        </Paper>
      </Container>
    </ThemeProvider>
  );
}

export default App; 