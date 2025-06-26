import React, { useState, useEffect } from 'react';
import {
  Box,
  Chip,
  Tooltip,
  CircularProgress
} from '@mui/material';
import { 
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Warning as WarningIcon
} from '@mui/icons-material';

const HealthStatus = () => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('http://localhost:8000/health');
        if (response.ok) {
          const data = await response.json();
          setStatus(data);
        } else {
          setStatus({ status: 'error', error: 'Backend unavailable' });
        }
      } catch (error) {
        setStatus({ 
          status: 'error', 
          error: 'Cannot connect to backend',
          groq_configured: false,
          mongodb_configured: false,
          mysql_configured: false
        });
      } finally {
        setLoading(false);
      }
    };

    checkHealth();
    
    // Check health every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
        <CircularProgress size={20} />
      </Box>
    );
  }

  const getStatusInfo = () => {
    if (status?.status === 'error') {
      return {
        label: 'Backend Offline',
        color: 'error',
        icon: <ErrorIcon />
      };
    }

    if (!status?.groq_configured || !status?.mongodb_configured) {
      return {
        label: 'Configuration Incomplete',
        color: 'warning', 
        icon: <WarningIcon />
      };
    }

    return {
      label: 'All Systems Online',
      color: 'success',
      icon: <CheckIcon />
    };
  };

  const statusInfo = getStatusInfo();

  const getTooltipContent = () => {
    if (status?.status === 'error') {
      return `Error: ${status.error}`;
    }

    const items = [
      `Backend: ${status?.status === 'healthy' ? '✅' : '❌'}`,
      `Groq API: ${status?.groq_configured ? '✅' : '❌'}`,
      `MongoDB: ${status?.mongodb_configured ? '✅' : '❌'}`,
      `MySQL: ${status?.mysql_configured ? '✅' : '⚠️ Optional'}`
    ];

    return items.join('\n');
  };

  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
      <Tooltip 
        title={getTooltipContent()}
        arrow
        sx={{ whiteSpace: 'pre-line' }}
      >
        <Chip
          icon={statusInfo.icon}
          label={statusInfo.label}
          color={statusInfo.color}
          variant="outlined"
          size="small"
        />
      </Tooltip>
    </Box>
  );
};

export default HealthStatus; 