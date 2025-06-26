import React from 'react';
import {
  Box,
  Typography,
  Alert,
  CircularProgress,
  Chip
} from '@mui/material';
import { 
  TextFields as TextIcon,
  TableChart as TableIcon,
  BarChart as ChartIcon
} from '@mui/icons-material';
import DataTable from './DataTable';
import DataChart from './DataChart';

const ResultDisplay = ({ result, loading, error }) => {
  if (loading) {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 4 }}>
        <CircularProgress size={40} sx={{ mb: 2 }} />
        <Typography variant="body1" color="text.secondary">
          Processing your query with Groq AI...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        <Typography variant="body1">
          <strong>Error:</strong> {error}
        </Typography>
        <Typography variant="body2" sx={{ mt: 1 }}>
          Please check your backend connection and try again.
        </Typography>
      </Alert>
    );
  }

  if (!result) {
    return null;
  }

  const getTypeIcon = (type) => {
    switch (type) {
      case 'table':
        return <TableIcon />;
      case 'chart':
        return <ChartIcon />;
      default:
        return <TextIcon />;
    }
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'table':
        return 'primary';
      case 'chart':
        return 'secondary';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          Results
        </Typography>
        <Chip 
          icon={getTypeIcon(result.type)}
          label={result.type.charAt(0).toUpperCase() + result.type.slice(1)}
          color={getTypeColor(result.type)}
          variant="outlined"
        />
      </Box>

      {result.type === 'text' && (
        <Box sx={{ 
          bgcolor: 'grey.50', 
          p: 2, 
          borderRadius: 1,
          borderLeft: 4,
          borderColor: 'primary.main'
        }}>
          <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
            {result.data}
          </Typography>
        </Box>
      )}

      {result.type === 'table' && (
        <DataTable data={result.data} metadata={result.metadata} />
      )}

      {result.type === 'chart' && (
        <DataChart data={result.data} metadata={result.metadata} />
      )}

      {result.metadata && (
        <Box sx={{ mt: 2, p: 1.5, bgcolor: 'grey.100', borderRadius: 1 }}>
          <Typography variant="caption" color="text.secondary">
            {result.metadata.question && `Question: ${result.metadata.question}`}
            {result.metadata.rows && ` • Rows: ${result.metadata.rows}`}
            {result.metadata.data_points && ` • Data Points: ${result.metadata.data_points}`}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default ResultDisplay; 