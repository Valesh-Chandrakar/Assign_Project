import React, { useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Line, Pie } from 'react-chartjs-2';
import { Box, Typography, Paper } from '@mui/material';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const DataChart = ({ data, metadata }) => {
  const chartConfig = useMemo(() => {
    if (!data || !data.data || !Array.isArray(data.data)) {
      return null;
    }

    const labels = data.data.map(item => item.label);
    const values = data.data.map(item => item.value);
    
    // Generate colors for chart
    const backgroundColors = [
      'rgba(54, 162, 235, 0.6)',
      'rgba(255, 99, 132, 0.6)',
      'rgba(255, 206, 86, 0.6)',
      'rgba(75, 192, 192, 0.6)',
      'rgba(153, 102, 255, 0.6)',
      'rgba(255, 159, 64, 0.6)',
      'rgba(199, 199, 199, 0.6)',
      'rgba(83, 102, 255, 0.6)',
    ];

    const borderColors = [
      'rgba(54, 162, 235, 1)',
      'rgba(255, 99, 132, 1)', 
      'rgba(255, 206, 86, 1)',
      'rgba(75, 192, 192, 1)',
      'rgba(153, 102, 255, 1)',
      'rgba(255, 159, 64, 1)',
      'rgba(199, 199, 199, 1)',
      'rgba(83, 102, 255, 1)',
    ];

    const chartData = {
      labels,
      datasets: [
        {
          label: data.y_label || 'Value',
          data: values,
          backgroundColor: data.chart_type === 'pie' 
            ? backgroundColors.slice(0, values.length)
            : backgroundColors[0],
          borderColor: data.chart_type === 'pie'
            ? borderColors.slice(0, values.length)
            : borderColors[0],
          borderWidth: 2,
          tension: 0.4, // For line charts
        },
      ],
    };

    const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: data.chart_type === 'pie' ? 'right' : 'top',
          display: true,
        },
        title: {
          display: !!data.title,
          text: data.title,
          font: {
            size: 16,
            weight: 'bold',
          },
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const label = context.dataset.label || '';
              const value = context.parsed.y !== undefined ? context.parsed.y : context.parsed;
              
              // Format currency values
              if (data.y_label && data.y_label.includes('$')) {
                return `${label}: $${value.toLocaleString()}`;
              }
              
              // Format percentage values
              if (data.y_label && data.y_label.includes('%')) {
                return `${label}: ${value}%`;
              }
              
              return `${label}: ${value.toLocaleString()}`;
            }
          }
        }
      },
      scales: data.chart_type !== 'pie' ? {
        x: {
          title: {
            display: !!data.x_label,
            text: data.x_label,
          },
        },
        y: {
          title: {
            display: !!data.y_label,
            text: data.y_label,
          },
          beginAtZero: true,
        },
      } : {},
    };

    return { chartData, options, type: data.chart_type };
  }, [data]);

  if (!chartConfig) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="body1" color="text.secondary">
          No chart data available
        </Typography>
      </Box>
    );
  }

  const renderChart = () => {
    const { chartData, options, type } = chartConfig;
    
    switch (type) {
      case 'bar':
        return <Bar data={chartData} options={options} />;
      case 'line':
        return <Line data={chartData} options={options} />;
      case 'pie':
        return <Pie data={chartData} options={options} />;
      default:
        return <Bar data={chartData} options={options} />;
    }
  };

  return (
    <Paper variant="outlined" sx={{ p: 2 }}>
      <Box sx={{ height: 400, position: 'relative' }}>
        {renderChart()}
      </Box>
      
      {data.data && data.data.length > 0 && (
        <Box sx={{ mt: 2, p: 1.5, bgcolor: 'grey.50', borderRadius: 1 }}>
          <Typography variant="caption" color="text.secondary">
            Chart Type: {data.chart_type || 'bar'} • 
            Data Points: {data.data.length} • 
            Range: {Math.min(...data.data.map(d => d.value)).toLocaleString()} - {Math.max(...data.data.map(d => d.value)).toLocaleString()}
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default DataChart; 