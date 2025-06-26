import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Grid,
  Chip
} from '@mui/material';
import { 
  Psychology as AiIcon,
  TrendingUp as TrendIcon,
  People as PeopleIcon,
  AccountBalance as AccountIcon
} from '@mui/icons-material';

const ExampleQueries = ({ onExampleClick }) => {
  const [examples, setExamples] = useState([]);
  const [loading, setLoading] = useState(true);

  const defaultExamples = [
    {
      text: "Show me top 5 clients by equity value",
      category: "Portfolio",
      icon: <TrendIcon />
    },
    {
      text: "List clients from New York with investment preferences", 
      category: "Demographics",
      icon: <PeopleIcon />
    },
    {
      text: "What are the recent transactions for high-value portfolios?",
      category: "Transactions", 
      icon: <AccountIcon />
    },
    {
      text: "Compare portfolio performance over the last quarter",
      category: "Analysis",
      icon: <TrendIcon />
    },
    {
      text: "Show me the distribution of client age groups",
      category: "Demographics",
      icon: <PeopleIcon />
    },
    {
      text: "Which sectors have the highest returns this month?",
      category: "Analysis",
      icon: <TrendIcon />
    }
  ];

  useEffect(() => {
    const fetchExamples = async () => {
      try {
        const response = await fetch('http://localhost:8000/examples');
        if (response.ok) {
          const data = await response.json();
          const examplesWithMetadata = data.examples.map((example, index) => ({
            text: example,
            category: defaultExamples[index]?.category || "General",
            icon: defaultExamples[index]?.icon || <AiIcon />
          }));
          setExamples(examplesWithMetadata);
        } else {
          setExamples(defaultExamples);
        }
      } catch (error) {
        console.error('Failed to fetch examples:', error);
        setExamples(defaultExamples);
      } finally {
        setLoading(false);
      }
    };

    fetchExamples();
  }, []);

  const getCategoryColor = (category) => {
    switch (category) {
      case 'Portfolio':
        return 'primary';
      case 'Demographics':
        return 'secondary';
      case 'Transactions':
        return 'success';
      case 'Analysis':
        return 'info';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box sx={{ textAlign: 'center', py: 2 }}>
        <Typography variant="body2" color="text.secondary">
          Loading examples...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
        💡 Example Queries
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Click on any example below to try it out:
      </Typography>

      <Grid container spacing={2}>
        {examples.map((example, index) => (
          <Grid item xs={12} md={6} key={index}>
            <Button
              variant="outlined"
              fullWidth
              onClick={() => onExampleClick(example.text)}
              sx={{
                p: 2,
                textAlign: 'left',
                justifyContent: 'flex-start',
                textTransform: 'none',
                borderRadius: 2,
                minHeight: 80,
                '&:hover': {
                  backgroundColor: 'action.hover',
                }
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'flex-start', width: '100%' }}>
                <Box sx={{ mr: 1.5, color: 'primary.main', flexShrink: 0 }}>
                  {example.icon}
                </Box>
                <Box sx={{ flexGrow: 1 }}>
                  <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
                    {example.text}
                  </Typography>
                  <Chip 
                    label={example.category}
                    size="small"
                    color={getCategoryColor(example.category)}
                    variant="outlined"
                  />
                </Box>
              </Box>
            </Button>
          </Grid>
        ))}
      </Grid>

      <Box sx={{ mt: 3, p: 2, bgcolor: 'info.light', borderRadius: 1 }}>
        <Typography variant="body2" color="info.dark">
          <strong>💡 Tips:</strong> You can ask about client information (stored in MongoDB) 
          or portfolio/transaction data (stored in MySQL). The AI will automatically choose 
          the right database and format the response as text, table, or chart.
        </Typography>
      </Box>
    </Box>
  );
};

export default ExampleQueries; 