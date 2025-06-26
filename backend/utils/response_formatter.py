import re
import json
from typing import Dict, Any, List, Union
import pandas as pd

class ResponseFormatter:
    """Formats agent responses into structured format for frontend consumption"""
    
    def __init__(self):
        self.chart_keywords = [
            "chart", "graph", "plot", "visualization", "compare", "comparison", 
            "distribution", "trend", "performance", "top", "ranking", "vs"
        ]
        self.table_keywords = [
            "list", "table", "records", "entries", "details", "show me", 
            "portfolio", "transactions", "clients"
        ]
    
    def format_response(self, question: str, agent_output: str) -> Dict[str, Any]:
        """
        Format agent output into structured response
        Returns dict with type, data, and metadata
        """
        # Determine response type based on question and output content
        response_type = self._determine_response_type(question, agent_output)
        
        if response_type == "table":
            return self._format_as_table(agent_output, question)
        elif response_type == "chart":
            return self._format_as_chart(agent_output, question)
        else:
            return self._format_as_text(agent_output, question)
    
    def _determine_response_type(self, question: str, output: str) -> str:
        """Determine if response should be text, table, or chart"""
        question_lower = question.lower()
        output_lower = output.lower()
        
        # Check for chart indicators
        chart_score = sum(1 for keyword in self.chart_keywords if keyword in question_lower)
        chart_score += sum(1 for keyword in ["top", "best", "worst", "compare", "vs"] if keyword in output_lower)
        
        # Check for table indicators  
        table_score = sum(1 for keyword in self.table_keywords if keyword in question_lower)
        table_score += sum(1 for keyword in ["records", "found", "list", "entries"] if keyword in output_lower)
        
        # Look for structured data patterns
        has_numbers = bool(re.search(r'\$[\d,]+|\d+\.\d+%|\d+', output))
        has_structured_data = bool(re.search(r'Name:|Age:|Value:|Record \d+', output))
        
        if chart_score > table_score and has_numbers:
            return "chart"
        elif table_score > 0 or has_structured_data:
            return "table"
        else:
            return "text"
    
    def _format_as_text(self, output: str, question: str) -> Dict[str, Any]:
        """Format as simple text response"""
        return {
            "type": "text",
            "data": output,
            "metadata": {
                "question": question,
                "response_length": len(output.split())
            }
        }
    
    def _format_as_table(self, output: str, question: str) -> Dict[str, Any]:
        """Extract tabular data from output"""
        try:
            # Try to parse structured data from the output
            table_data = self._extract_table_data(output)
            
            if table_data:
                return {
                    "type": "table",
                    "data": table_data,
                    "metadata": {
                        "question": question,
                        "rows": len(table_data),
                        "columns": list(table_data[0].keys()) if table_data else []
                    }
                }
            else:
                # Fallback to text if can't extract table
                return self._format_as_text(output, question)
                
        except Exception as e:
            print(f"Error formatting table: {e}")
            return self._format_as_text(output, question)
    
    def _format_as_chart(self, output: str, question: str) -> Dict[str, Any]:
        """Extract chart data from output"""
        try:
            # Extract numerical data for charting
            chart_data = self._extract_chart_data(output)
            
            if chart_data:
                # Determine chart type based on data structure
                chart_type = self._determine_chart_type(question, chart_data)
                
                return {
                    "type": "chart",
                    "data": {
                        "chart_type": chart_type,
                        "data": chart_data,
                        "title": self._generate_chart_title(question),
                        "x_label": self._extract_x_label(question, chart_data),
                        "y_label": self._extract_y_label(question, chart_data)
                    },
                    "metadata": {
                        "question": question,
                        "data_points": len(chart_data)
                    }
                }
            else:
                # Fallback to table or text
                return self._format_as_table(output, question)
                
        except Exception as e:
            print(f"Error formatting chart: {e}")
            return self._format_as_table(output, question)
    
    def _extract_table_data(self, output: str) -> List[Dict[str, Any]]:
        """Extract structured table data from text output"""
        rows = []
        
        # Pattern 0: Raw SQL query results (tuples)
        if 'datetime.date' in output and 'Decimal' in output and '[(' in output:
            rows = self._parse_sql_tuples(output)
            if rows:
                return rows
        
        # Pattern 1: Record-based format (MongoDB style)
        record_pattern = r'--- Record \d+ ---\n(.*?)(?=--- Record \d+ ---|$)'
        records = re.findall(record_pattern, output, re.DOTALL)
        
        if records:
            for record in records:
                row = {}
                # Extract key-value pairs
                lines = record.strip().split('\n')
                for line in lines:
                    if ':' in line and not line.strip().startswith(' '):
                        key, value = line.split(':', 1)
                        row[key.strip()] = value.strip()
                if row:
                    rows.append(row)
        
        # Pattern 2: List-based format
        elif re.search(r'\d+\.\s+.*?:', output):
            items = re.findall(r'\d+\.\s+(.*)', output)
            for item in items:
                row = {}
                # Try to extract key-value pairs from each item
                parts = item.split(',')
                for part in parts:
                    if ':' in part:
                        key, value = part.split(':', 1)
                        row[key.strip()] = value.strip()
                    else:
                        # If no key-value, use as description
                        row['Description'] = part.strip()
                if row:
                    rows.append(row)
        
        # Pattern 3: SQL-style results
        elif 'Found' in output and any(char in output for char in ['$', '%', 'Value']):
            lines = output.split('\n')
            for line in lines:
                if any(indicator in line for indicator in ['Name:', 'Client:', 'Portfolio:']):
                    row = {}
                    # Extract key-value pairs from the line
                    parts = re.findall(r'(\w+):\s*([^,\n]+)', line)
                    for key, value in parts:
                        row[key.strip()] = value.strip()
                    if row:
                        rows.append(row)
        
        return rows
    
    def _parse_sql_tuples(self, output: str) -> List[Dict[str, Any]]:
        """Parse raw SQL query results from tuple format"""
        rows = []
        
        try:
            # Extract the list of tuples from the output
            tuple_start = output.find('[')
            tuple_end = output.rfind(']') + 1
            if tuple_start == -1 or tuple_end == 0:
                return rows
            
            tuple_str = output[tuple_start:tuple_end]
            
            # Try to safely evaluate the string as Python data
            # This is risky in general but controlled in this context
            import ast
            from datetime import datetime, date
            from decimal import Decimal
            
            # Replace the problematic parts for parsing
            tuple_str = tuple_str.replace('datetime.date', 'date')
            tuple_str = tuple_str.replace('datetime.datetime', 'datetime')
            tuple_str = tuple_str.replace('Decimal(', 'float(')
            
            try:
                # Parse the tuples
                data_tuples = eval(tuple_str, {
                    "date": date,
                    "datetime": datetime,
                    "Decimal": Decimal,
                    "float": float
                })
                
                if not data_tuples:
                    return rows
                
                # Determine column names based on context
                # For market_data table based on the structure seen
                if len(data_tuples[0]) == 10:
                    columns = [
                        "ID", "Security ID", "Date", "Open Price", "High Price", 
                        "Low Price", "Close Price", "Volume", "Adjusted Close", "Created At"
                    ]
                else:
                    # Generic column names
                    columns = [f"Column {i+1}" for i in range(len(data_tuples[0]))]
                
                # Convert tuples to dictionaries
                for row_tuple in data_tuples:
                    row_dict = {}
                    for i, value in enumerate(row_tuple):
                        column_name = columns[i] if i < len(columns) else f"Column {i+1}"
                        
                        # Format the value appropriately
                        if value is None:
                            formatted_value = "N/A"
                        elif isinstance(value, (Decimal, float)) and "Price" in column_name:
                            formatted_value = f"${float(value):,.2f}"
                        elif isinstance(value, (Decimal, float)):
                            formatted_value = f"{float(value):,.2f}"
                        elif isinstance(value, (date, datetime)):
                            formatted_value = value.strftime("%Y-%m-%d")
                        elif isinstance(value, int) and "Volume" in column_name:
                            formatted_value = f"{value:,}"
                        else:
                            formatted_value = str(value)
                        
                        row_dict[column_name] = formatted_value
                    
                    rows.append(row_dict)
                    
            except (SyntaxError, ValueError, NameError) as e:
                print(f"Error parsing SQL tuples: {e}")
                return []
                
        except Exception as e:
            print(f"Error processing SQL tuples: {e}")
            return []
        
        return rows
    
    def _extract_chart_data(self, output: str) -> List[Dict[str, Any]]:
        """Extract numerical data suitable for charting"""
        chart_data = []
        
        # Look for numerical patterns with labels
        patterns = [
            r'(\w+(?:\s+\w+)*?):\s*\$?([\d,]+\.?\d*)',  # Name: $1,234.56
            r'(\d+)\.\s+([^:]+):\s*\$?([\d,]+\.?\d*)',   # 1. Name: $1,234.56
            r'([A-Za-z\s]+?)\s*-\s*\$?([\d,]+\.?\d*)',   # Name - $1,234.56
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, output)
            if matches:
                for match in matches:
                    if len(match) == 2:
                        label, value_str = match
                    elif len(match) == 3:
                        _, label, value_str = match
                    else:
                        continue
                    
                    # Clean up the value
                    value_str = value_str.replace(',', '')
                    try:
                        value = float(value_str)
                        chart_data.append({
                            "label": label.strip(),
                            "value": value
                        })
                    except ValueError:
                        continue
                
                if chart_data:
                    break
        
        # If no structured data found, try to extract from table data
        if not chart_data:
            table_data = self._extract_table_data(output)
            if table_data:
                # Try to find numerical columns
                for row in table_data:
                    for key, value in row.items():
                        if isinstance(value, str) and ('$' in value or value.replace(',', '').replace('.', '').isdigit()):
                            try:
                                numeric_value = float(value.replace('$', '').replace(',', ''))
                                # Use the first column as label, numeric column as value
                                label_key = list(row.keys())[0]
                                chart_data.append({
                                    "label": row.get(label_key, f"Item {len(chart_data) + 1}"),
                                    "value": numeric_value
                                })
                                break
                            except ValueError:
                                continue
        
        return chart_data
    
    def _determine_chart_type(self, question: str, data: List[Dict]) -> str:
        """Determine the most appropriate chart type"""
        question_lower = question.lower()
        
        if "distribution" in question_lower or "breakdown" in question_lower:
            return "pie"
        elif "compare" in question_lower or "vs" in question_lower:
            return "bar"
        elif "trend" in question_lower or "over time" in question_lower:
            return "line"
        elif "top" in question_lower or "ranking" in question_lower:
            return "bar"
        else:
            # Default to bar chart for most numerical comparisons
            return "bar"
    
    def _generate_chart_title(self, question: str) -> str:
        """Generate an appropriate chart title from the question"""
        # Clean up the question to make a nice title
        title = question.strip('?').title()
        if len(title) > 50:
            title = title[:47] + "..."
        return title
    
    def _extract_x_label(self, question: str, data: List[Dict]) -> str:
        """Extract appropriate X-axis label"""
        if "client" in question.lower():
            return "Clients"
        elif "portfolio" in question.lower():
            return "Portfolios"
        elif "sector" in question.lower():
            return "Sectors"
        else:
            return "Categories"
    
    def _extract_y_label(self, question: str, data: List[Dict]) -> str:
        """Extract appropriate Y-axis label"""
        if any("$" in str(item.get("value", "")) for item in data):
            return "Value ($)"
        elif "count" in question.lower() or "number" in question.lower():
            return "Count"
        elif "percentage" in question.lower() or "%" in question.lower():
            return "Percentage (%)"
        else:
            return "Value" 