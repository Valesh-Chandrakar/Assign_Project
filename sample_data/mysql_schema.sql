-- MySQL Database Schema for Portfolio Management System
-- Run this script to create the necessary tables for portfolio and transaction data

-- Create database (if not exists)
CREATE DATABASE IF NOT EXISTS portfolio_db;
USE portfolio_db;

-- Table: clients (basic client info for referencing with MongoDB)
CREATE TABLE IF NOT EXISTS clients (
    client_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_client_name (name),
    INDEX idx_client_email (email)
);

-- Table: portfolios
CREATE TABLE IF NOT EXISTS portfolios (
    portfolio_id INT AUTO_INCREMENT PRIMARY KEY,
    client_id VARCHAR(20) NOT NULL,
    portfolio_name VARCHAR(100) NOT NULL,
    portfolio_type ENUM('Individual', 'Joint', 'Corporate', 'Trust', 'IRA', '401k') DEFAULT 'Individual',
    total_value DECIMAL(15,2) DEFAULT 0.00,
    cash_balance DECIMAL(15,2) DEFAULT 0.00,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    status ENUM('Active', 'Inactive', 'Closed') DEFAULT 'Active',
    FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE,
    INDEX idx_client_portfolio (client_id),
    INDEX idx_portfolio_value (total_value),
    INDEX idx_portfolio_status (status)
);

-- Table: securities (stocks, bonds, ETFs, etc.)
CREATE TABLE IF NOT EXISTS securities (
    security_id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL UNIQUE,
    security_name VARCHAR(200) NOT NULL,
    security_type ENUM('Stock', 'Bond', 'ETF', 'Mutual Fund', 'Option', 'Crypto') NOT NULL,
    sector VARCHAR(50),
    industry VARCHAR(100),
    exchange VARCHAR(20),
    current_price DECIMAL(10,4),
    currency VARCHAR(3) DEFAULT 'USD',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_security_type (security_type),
    INDEX idx_sector (sector)
);

-- Table: portfolio_holdings
CREATE TABLE IF NOT EXISTS portfolio_holdings (
    holding_id INT AUTO_INCREMENT PRIMARY KEY,
    portfolio_id INT NOT NULL,
    security_id INT NOT NULL,
    quantity DECIMAL(15,6) NOT NULL,
    average_cost DECIMAL(10,4) NOT NULL,
    current_value DECIMAL(15,2),
    unrealized_gain_loss DECIMAL(15,2),
    percentage_of_portfolio DECIMAL(5,2),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE,
    FOREIGN KEY (security_id) REFERENCES securities(security_id) ON DELETE CASCADE,
    UNIQUE KEY unique_portfolio_security (portfolio_id, security_id),
    INDEX idx_portfolio_holdings (portfolio_id),
    INDEX idx_security_holdings (security_id)
);

-- Table: transactions
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    portfolio_id INT NOT NULL,
    security_id INT,
    transaction_type ENUM('Buy', 'Sell', 'Dividend', 'Deposit', 'Withdrawal', 'Fee', 'Interest') NOT NULL,
    quantity DECIMAL(15,6),
    price DECIMAL(10,4),
    total_amount DECIMAL(15,2) NOT NULL,
    fees DECIMAL(10,2) DEFAULT 0.00,
    transaction_date DATE NOT NULL,
    settlement_date DATE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE,
    FOREIGN KEY (security_id) REFERENCES securities(security_id) ON DELETE SET NULL,
    INDEX idx_portfolio_transactions (portfolio_id),
    INDEX idx_transaction_date (transaction_date),
    INDEX idx_transaction_type (transaction_type),
    INDEX idx_security_transactions (security_id)
);

-- Table: portfolio_performance
CREATE TABLE IF NOT EXISTS portfolio_performance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    portfolio_id INT NOT NULL,
    performance_date DATE NOT NULL,
    total_value DECIMAL(15,2) NOT NULL,
    daily_return DECIMAL(8,4),
    cumulative_return DECIMAL(8,4),
    benchmark_return DECIMAL(8,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE,
    UNIQUE KEY unique_portfolio_date (portfolio_id, performance_date),
    INDEX idx_portfolio_performance (portfolio_id),
    INDEX idx_performance_date (performance_date)
);

-- Table: market_data (for storing historical prices)
CREATE TABLE IF NOT EXISTS market_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    security_id INT NOT NULL,
    price_date DATE NOT NULL,
    open_price DECIMAL(10,4),
    high_price DECIMAL(10,4),
    low_price DECIMAL(10,4),
    close_price DECIMAL(10,4) NOT NULL,
    volume BIGINT,
    adjusted_close DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (security_id) REFERENCES securities(security_id) ON DELETE CASCADE,
    UNIQUE KEY unique_security_date (security_id, price_date),
    INDEX idx_security_price_date (security_id, price_date),
    INDEX idx_price_date (price_date)
);

-- Create views for common queries
CREATE OR REPLACE VIEW portfolio_summary AS
SELECT 
    p.portfolio_id,
    p.client_id,
    c.name as client_name,
    p.portfolio_name,
    p.portfolio_type,
    p.total_value,
    p.cash_balance,
    COUNT(ph.holding_id) as num_holdings,
    p.status,
    p.last_updated
FROM portfolios p
LEFT JOIN clients c ON p.client_id = c.client_id
LEFT JOIN portfolio_holdings ph ON p.portfolio_id = ph.portfolio_id
GROUP BY p.portfolio_id, p.client_id, c.name, p.portfolio_name, p.portfolio_type, 
         p.total_value, p.cash_balance, p.status, p.last_updated;

CREATE OR REPLACE VIEW top_holdings AS
SELECT 
    ph.portfolio_id,
    p.client_id,
    c.name as client_name,
    s.symbol,
    s.security_name,
    s.sector,
    ph.quantity,
    ph.current_value,
    ph.percentage_of_portfolio,
    ph.unrealized_gain_loss
FROM portfolio_holdings ph
JOIN portfolios p ON ph.portfolio_id = p.portfolio_id
JOIN clients c ON p.client_id = c.client_id
JOIN securities s ON ph.security_id = s.security_id
WHERE ph.current_value > 0
ORDER BY ph.current_value DESC;

-- Add some useful stored procedures
DELIMITER //

CREATE PROCEDURE GetPortfoliosByValue(IN min_value DECIMAL(15,2))
BEGIN
    SELECT 
        ps.*,
        RANK() OVER (ORDER BY ps.total_value DESC) as value_rank
    FROM portfolio_summary ps 
    WHERE ps.total_value >= min_value
    ORDER BY ps.total_value DESC;
END //

CREATE PROCEDURE GetTopClientsByEquity(IN limit_count INT)
BEGIN
    SELECT 
        c.client_id,
        c.name,
        SUM(p.total_value) as total_equity,
        COUNT(p.portfolio_id) as num_portfolios,
        AVG(p.total_value) as avg_portfolio_value
    FROM clients c
    JOIN portfolios p ON c.client_id = p.client_id
    WHERE p.status = 'Active'
    GROUP BY c.client_id, c.name
    ORDER BY total_equity DESC
    LIMIT limit_count;
END //

DELIMITER ;

-- Create indexes for optimization
CREATE INDEX idx_transactions_date_type ON transactions(transaction_date, transaction_type);
CREATE INDEX idx_holdings_value ON portfolio_holdings(current_value);
CREATE INDEX idx_portfolio_client_status ON portfolios(client_id, status);

SHOW TABLES; 