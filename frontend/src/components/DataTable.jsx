import React, { useMemo } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Box,
  Chip
} from '@mui/material';

const DataTable = ({ data, metadata }) => {
  const tableData = useMemo(() => {
    if (!Array.isArray(data) || data.length === 0) {
      return { columns: [], rows: [] };
    }

    // Get all unique column names from all rows
    const allColumns = new Set();
    data.forEach(row => {
      Object.keys(row).forEach(key => allColumns.add(key));
    });

    const columns = Array.from(allColumns);
    
    return {
      columns,
      rows: data
    };
  }, [data]);

  if (!data || data.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="body1" color="text.secondary">
          No data to display
        </Typography>
      </Box>
    );
  }

  const formatCellValue = (value) => {
    if (value === null || value === undefined) {
      return '-';
    }
    
    if (typeof value === 'object') {
      return JSON.stringify(value);
    }
    
    // Format currency
    if (typeof value === 'string' && value.includes('$')) {
      return value;
    }
    
    // Format large numbers
    if (typeof value === 'number' && value > 1000) {
      return value.toLocaleString();
    }
    
    return String(value);
  };

  const getCellColor = (column, value) => {
    // Color code certain types of data
    if (column.toLowerCase().includes('value') || column.toLowerCase().includes('amount')) {
      return 'success.main';
    }
    if (column.toLowerCase().includes('risk')) {
      if (String(value).toLowerCase().includes('high')) return 'error.main';
      if (String(value).toLowerCase().includes('low')) return 'success.main';
      if (String(value).toLowerCase().includes('medium')) return 'warning.main';
    }
    return 'text.primary';
  };

  return (
    <Box>
      <TableContainer component={Paper} variant="outlined">
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              {tableData.columns.map((column) => (
                <TableCell 
                  key={column}
                  sx={{ 
                    fontWeight: 'bold',
                    backgroundColor: 'primary.main',
                    color: 'primary.contrastText'
                  }}
                >
                  {column.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {tableData.rows.map((row, index) => (
              <TableRow 
                key={index}
                hover
                sx={{ '&:nth-of-type(odd)': { backgroundColor: 'action.hover' } }}
              >
                {tableData.columns.map((column) => (
                  <TableCell 
                    key={column}
                    sx={{ 
                      color: getCellColor(column, row[column]),
                      maxWidth: 200,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }}
                  >
                    {column.toLowerCase().includes('risk') && row[column] ? (
                      <Chip 
                        label={formatCellValue(row[column])}
                        size="small"
                        color={
                          String(row[column]).toLowerCase().includes('high') ? 'error' :
                          String(row[column]).toLowerCase().includes('low') ? 'success' :
                          String(row[column]).toLowerCase().includes('medium') ? 'warning' : 'default'
                        }
                      />
                    ) : (
                      formatCellValue(row[column])
                    )}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      
      {tableData.rows.length > 10 && (
        <Box sx={{ mt: 1, textAlign: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            Showing {Math.min(10, tableData.rows.length)} of {tableData.rows.length} results
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default DataTable; 