import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  CircularProgress
} from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';

const QueryInput = ({ onSubmit, loading }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim() && !loading) {
      onSubmit(query.trim());
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Ask a Question
      </Typography>
      <form onSubmit={handleSubmit}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-end' }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="e.g., Show me top 5 clients by equity value"
            variant="outlined"
            disabled={loading}
            sx={{ flexGrow: 1 }}
          />
          <Button
            type="submit"
            variant="contained"
            disabled={!query.trim() || loading}
            endIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
            sx={{ 
              minWidth: 120,
              height: 56 // Match TextField height
            }}
          >
            {loading ? 'Asking...' : 'Ask'}
          </Button>
        </Box>
      </form>
      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
        💡 Try asking about client demographics, portfolio performance, or transaction history
      </Typography>
    </Box>
  );
};

export default QueryInput; 