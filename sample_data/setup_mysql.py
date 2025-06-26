#!/usr/bin/env python3
"""
MySQL Database Setup Script for Portfolio Management System
This script helps you set up the MySQL database with schema and sample data.
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
from pathlib import Path

def get_database_config():
    """Get database configuration from environment or user input"""
    config = {}
    
    # Check if MYSQL_URI is set
    mysql_uri = os.getenv('MYSQL_URI')
    if mysql_uri:
        print("📌 Using MYSQL_URI from environment variables")
        # Parse the URI (format: mysql+pymysql://user:password@host:port/database)
        if mysql_uri.startswith('mysql+pymysql://'):
            uri = mysql_uri.replace('mysql+pymysql://', '')
            if '@' in uri:
                credentials, host_db = uri.split('@')
                if ':' in credentials:
                    config['user'], config['password'] = credentials.split(':')
                if '/' in host_db:
                    host_port, config['database'] = host_db.split('/')
                    if ':' in host_port:
                        config['host'], port = host_port.split(':')
                        config['port'] = int(port)
                    else:
                        config['host'] = host_port
                        config['port'] = 3306
    else:
        print("⚠️  MYSQL_URI not found in environment variables")
        print("Please provide MySQL connection details:")
        config['host'] = input("Host (default: localhost): ") or 'localhost'
        config['port'] = int(input("Port (default: 3306): ") or 3306)
        config['user'] = input("Username: ")
        config['password'] = input("Password: ")
        config['database'] = input("Database name (default: portfolio_db): ") or 'portfolio_db'
    
    return config

def connect_to_mysql(config):
    """Connect to MySQL server"""
    try:
        # First connect without database to create it if needed
        connection = mysql.connector.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password']
        )
        
        if connection.is_connected():
            print(f"✅ Connected to MySQL server at {config['host']}")
            return connection
            
    except Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
        return None

def execute_sql_file(connection, file_path):
    """Execute SQL commands from a file"""
    try:
        cursor = connection.cursor()
        
        with open(file_path, 'r') as file:
            sql_commands = file.read()
        
        # Split commands by semicolon and execute individually
        commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip()]
        
        for command in commands:
            if command:
                try:
                    cursor.execute(command)
                    connection.commit()
                except Error as e:
                    if "already exists" not in str(e).lower():
                        print(f"⚠️  Warning executing command: {e}")
        
        cursor.close()
        print(f"✅ Successfully executed {file_path}")
        return True
        
    except Error as e:
        print(f"❌ Error executing {file_path}: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return False

def main():
    """Main setup function"""
    print("🛠️  MySQL Database Setup for Portfolio Management System")
    print("=" * 60)
    
    # Get database configuration
    config = get_database_config()
    
    # Connect to MySQL
    connection = connect_to_mysql(config)
    if not connection:
        print("❌ Failed to connect to MySQL. Exiting.")
        return False
    
    try:
        # Define file paths
        current_dir = Path(__file__).parent
        schema_file = current_dir / "mysql_schema.sql"
        data_file = current_dir / "mysql_sample_data.sql"
        
        # Check if files exist
        if not schema_file.exists():
            print(f"❌ Schema file not found: {schema_file}")
            return False
        
        if not data_file.exists():
            print(f"❌ Sample data file not found: {data_file}")
            return False
        
        # Execute schema file
        print("\n🔧 Creating database schema...")
        if not execute_sql_file(connection, schema_file):
            print("❌ Failed to create schema. Exiting.")
            return False
        
        # Ask user if they want to insert sample data
        print("\n📊 Would you like to insert sample data?")
        insert_data = input("This will add realistic portfolio and transaction data (y/N): ").lower()
        
        if insert_data in ['y', 'yes']:
            print("\n📥 Inserting sample data...")
            if not execute_sql_file(connection, data_file):
                print("❌ Failed to insert sample data.")
                return False
        else:
            print("⏭️  Skipping sample data insertion")
        
        print("\n🎉 MySQL database setup completed successfully!")
        print("\n📋 What was created:")
        print("• Database: portfolio_db")
        print("• Tables: clients, portfolios, securities, portfolio_holdings, transactions, portfolio_performance, market_data")
        print("• Views: portfolio_summary, top_holdings")
        print("• Stored Procedures: GetPortfoliosByValue, GetTopClientsByEquity")
        
        if insert_data in ['y', 'yes']:
            print("• Sample data: 15 clients, 16 portfolios, 23 securities, portfolio holdings, transactions")
        
        print(f"\n🔗 Connection String: mysql+pymysql://{config['user']}:***@{config['host']}:{config['port']}/{config['database']}")
        print("\n💡 You can now update your backend/.env file with the MYSQL_URI")
        
        return True
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
        
    finally:
        if connection.is_connected():
            connection.close()
            print("🔌 MySQL connection closed")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 