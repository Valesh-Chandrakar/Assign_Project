-- Sample Data for Portfolio Management System
-- Run this after creating the database schema (mysql_schema.sql)

USE portfolio_db;

-- Insert sample clients (these should match some client_ids from MongoDB)
INSERT INTO clients (client_id, name, email) VALUES
('CLT1001', 'John Smith', 'john.smith@email.com'),
('CLT1002', 'Jane Johnson', 'jane.johnson@email.com'),
('CLT1003', 'Michael Williams', 'michael.williams@email.com'),
('CLT1004', 'Sarah Brown', 'sarah.brown@email.com'),
('CLT1005', 'David Jones', 'david.jones@email.com'),
('CLT1006', 'Lisa Garcia', 'lisa.garcia@email.com'),
('CLT1007', 'Robert Miller', 'robert.miller@email.com'),
('CLT1008', 'Emma Davis', 'emma.davis@email.com'),
('CLT1009', 'William Rodriguez', 'william.rodriguez@email.com'),
('CLT1010', 'Olivia Martinez', 'olivia.martinez@email.com'),
('CLT1011', 'James Hernandez', 'james.hernandez@email.com'),
('CLT1012', 'Sophia Lopez', 'sophia.lopez@email.com'),
('CLT1013', 'Alexander Gonzalez', 'alexander.gonzalez@email.com'),
('CLT1014', 'Isabella Wilson', 'isabella.wilson@email.com'),
('CLT1015', 'Benjamin Anderson', 'benjamin.anderson@email.com');

-- Insert sample securities
INSERT INTO securities (symbol, security_name, security_type, sector, industry, exchange, current_price) VALUES
-- Technology Stocks
('AAPL', 'Apple Inc.', 'Stock', 'Technology', 'Consumer Electronics', 'NASDAQ', 175.43),
('MSFT', 'Microsoft Corporation', 'Stock', 'Technology', 'Software', 'NASDAQ', 415.26),
('GOOGL', 'Alphabet Inc. Class A', 'Stock', 'Technology', 'Internet Services', 'NASDAQ', 141.68),
('AMZN', 'Amazon.com Inc.', 'Stock', 'Technology', 'E-commerce', 'NASDAQ', 144.73),
('META', 'Meta Platforms Inc.', 'Stock', 'Technology', 'Social Media', 'NASDAQ', 296.42),
('TSLA', 'Tesla Inc.', 'Stock', 'Technology', 'Electric Vehicles', 'NASDAQ', 248.50),
('NVDA', 'NVIDIA Corporation', 'Stock', 'Technology', 'Semiconductors', 'NASDAQ', 875.28),

-- Financial Stocks
('JPM', 'JPMorgan Chase & Co.', 'Stock', 'Finance', 'Banking', 'NYSE', 165.44),
('BAC', 'Bank of America Corp', 'Stock', 'Finance', 'Banking', 'NYSE', 34.82),
('WFC', 'Wells Fargo & Company', 'Stock', 'Finance', 'Banking', 'NYSE', 42.15),
('GS', 'Goldman Sachs Group Inc', 'Stock', 'Finance', 'Investment Banking', 'NYSE', 394.67),

-- Healthcare Stocks
('JNJ', 'Johnson & Johnson', 'Stock', 'Healthcare', 'Pharmaceuticals', 'NYSE', 160.25),
('PFE', 'Pfizer Inc.', 'Stock', 'Healthcare', 'Pharmaceuticals', 'NYSE', 28.44),
('UNH', 'UnitedHealth Group Inc', 'Stock', 'Healthcare', 'Health Insurance', 'NYSE', 524.18),

-- Consumer Goods
('KO', 'The Coca-Cola Company', 'Stock', 'Consumer Goods', 'Beverages', 'NYSE', 60.89),
('PG', 'Procter & Gamble Co', 'Stock', 'Consumer Goods', 'Personal Care', 'NYSE', 156.23),

-- Energy
('XOM', 'Exxon Mobil Corporation', 'Stock', 'Energy', 'Oil & Gas', 'NYSE', 104.65),
('CVX', 'Chevron Corporation', 'Stock', 'Energy', 'Oil & Gas', 'NYSE', 158.42),

-- ETFs
('SPY', 'SPDR S&P 500 ETF Trust', 'ETF', 'Diversified', 'Index Fund', 'NYSE', 445.67),
('QQQ', 'Invesco QQQ Trust', 'ETF', 'Technology', 'Tech Index Fund', 'NASDAQ', 375.45),
('VTI', 'Vanguard Total Stock Market ETF', 'ETF', 'Diversified', 'Total Market', 'NYSE', 234.56),
('VXUS', 'Vanguard Total International Stock ETF', 'ETF', 'International', 'Global Index', 'NYSE', 58.23),

-- Bonds
('TLT', 'iShares 20+ Year Treasury Bond ETF', 'ETF', 'Fixed Income', 'Government Bonds', 'NASDAQ', 94.32),
('LQD', 'iShares iBoxx Investment Grade Corporate Bond ETF', 'ETF', 'Fixed Income', 'Corporate Bonds', 'NYSE', 115.67);

-- Insert sample portfolios
INSERT INTO portfolios (client_id, portfolio_name, portfolio_type, total_value, cash_balance, status) VALUES
('CLT1001', 'John Smith Growth Portfolio', 'Individual', 1250000.00, 50000.00, 'Active'),
('CLT1001', 'John Smith Conservative IRA', 'IRA', 850000.00, 25000.00, 'Active'),
('CLT1002', 'Jane Johnson Tech Portfolio', 'Individual', 2100000.00, 75000.00, 'Active'),
('CLT1003', 'Michael Williams Balanced Fund', 'Individual', 750000.00, 30000.00, 'Active'),
('CLT1004', 'Sarah Brown Retirement Account', '401k', 950000.00, 40000.00, 'Active'),
('CLT1005', 'David Jones Investment Portfolio', 'Individual', 1650000.00, 60000.00, 'Active'),
('CLT1006', 'Lisa Garcia Family Trust', 'Trust', 3200000.00, 120000.00, 'Active'),
('CLT1007', 'Robert Miller Dividend Portfolio', 'Individual', 1100000.00, 45000.00, 'Active'),
('CLT1008', 'Emma Davis Growth & Income', 'Individual', 890000.00, 35000.00, 'Active'),
('CLT1009', 'William Rodriguez Conservative Mix', 'Individual', 1350000.00, 55000.00, 'Active'),
('CLT1010', 'Olivia Martinez Tech Growth', 'Individual', 1850000.00, 70000.00, 'Active'),
('CLT1011', 'James Hernandez Balanced Portfolio', 'Individual', 675000.00, 25000.00, 'Active'),
('CLT1012', 'Sophia Lopez ESG Portfolio', 'Individual', 1450000.00, 50000.00, 'Active'),
('CLT1013', 'Alexander Gonzalez Aggressive Growth', 'Individual', 2250000.00, 85000.00, 'Active'),
('CLT1014', 'Isabella Wilson Income Focus', 'Individual', 980000.00, 40000.00, 'Active'),
('CLT1015', 'Benjamin Anderson Diversified', 'Individual', 1150000.00, 45000.00, 'Active');

-- Insert sample portfolio holdings
INSERT INTO portfolio_holdings (portfolio_id, security_id, quantity, average_cost, current_value, unrealized_gain_loss, percentage_of_portfolio) VALUES
-- Portfolio 1 (John Smith Growth) - $1,200,000 invested
(1, 1, 1500, 145.20, 263145.00, 45345.00, 21.93), -- AAPL
(1, 2, 800, 380.50, 332208.00, 27808.00, 27.68), -- MSFT
(1, 4, 1200, 135.40, 173676.00, 11076.00, 14.47), -- AMZN
(1, 7, 300, 780.20, 262584.00, 28584.00, 21.88), -- NVDA
(1, 18, 500, 425.30, 222835.00, 10335.00, 18.57), -- SPY

-- Portfolio 2 (John Smith IRA) - $825,000 invested  
(2, 18, 1000, 435.20, 445670.00, 10470.00, 54.02), -- SPY
(2, 20, 1500, 230.80, 351840.00, 5640.00, 42.64), -- VTI
(2, 22, 300, 96.50, 28296.00, -954.00, 3.43), -- TLT

-- Portfolio 3 (Jane Johnson Tech) - $2,025,000 invested
(3, 1, 3000, 155.30, 526290.00, 60690.00, 26.00), -- AAPL
(3, 2, 1500, 395.80, 622890.00, 29140.00, 30.76), -- MSFT
(3, 3, 2000, 128.90, 283360.00, 25560.00, 13.99), -- GOOGL
(3, 5, 1000, 285.20, 296420.00, 11220.00, 14.64), -- META
(3, 6, 800, 230.75, 198800.00, 14000.00, 9.82), -- TSLA
(3, 7, 120, 820.50, 105033.60, 6549.60, 5.19), -- NVDA

-- Portfolio 4 (Michael Williams Balanced) - $720,000 invested
(4, 18, 800, 440.20, 356536.00, 3336.00, 49.52), -- SPY
(4, 12, 1000, 158.80, 160250.00, 1450.00, 22.26), -- JNJ
(4, 14, 2000, 60.20, 121780.00, 2580.00, 16.91), -- KO
(4, 23, 800, 118.50, 92536.00, -1264.00, 12.85), -- LQD

-- Portfolio 5 (Sarah Brown 401k) - $910,000 invested
(5, 18, 1200, 442.80, 535004.00, 3764.00, 58.79), -- SPY
(5, 19, 600, 372.20, 225270.00, 2070.00, 24.75), -- QQQ
(5, 20, 500, 236.40, 117280.00, -920.00, 12.89), -- VTI
(5, 21, 600, 59.80, 34938.00, -942.00, 3.84), -- VXUS

-- Continue with more holdings for other portfolios...
-- Portfolio 6 (David Jones) - $1,590,000 invested
(6, 1, 2000, 165.30, 350860.00, 20060.00, 22.07), -- AAPL
(6, 8, 3000, 155.20, 496320.00, 30720.00, 31.21), -- JPM
(6, 13, 1500, 510.80, 786270.00, 51720.00, 49.45), -- UNH
(6, 18, 400, 438.90, 178268.00, 2668.00, 11.21), -- SPY

-- Portfolio 7 (Lisa Garcia Trust) - $3,080,000 invested  
(7, 1, 4000, 162.20, 701720.00, 52920.00, 22.78), -- AAPL
(7, 2, 2500, 405.30, 1038150.00, 25150.00, 33.71), -- MSFT
(7, 8, 3500, 158.40, 579040.00, 25040.00, 18.80), -- JPM
(7, 11, 2000, 385.50, 789340.00, 18340.00, 25.63), -- GS
(7, 18, 800, 441.20, 356536.00, 3336.00, 11.58), -- SPY

-- Add more holdings for remaining portfolios...
-- Portfolio 13 (Alexander Gonzalez Aggressive) - $2,165,000 invested
(13, 6, 2500, 235.80, 621250.00, 32250.00, 28.70), -- TSLA
(13, 7, 800, 845.20, 700224.00, 24224.00, 32.34), -- NVDA
(13, 3, 3000, 135.20, 425040.00, 19440.00, 19.63), -- GOOGL
(13, 5, 1500, 278.90, 444630.00, 26280.00, 20.54); -- META

-- Insert sample transactions (last 6 months)
INSERT INTO transactions (portfolio_id, security_id, transaction_type, quantity, price, total_amount, fees, transaction_date, description) VALUES
-- Recent purchases
(1, 1, 'Buy', 500, 172.30, 86150.00, 9.95, '2024-01-15', 'AAPL purchase'),
(1, 2, 'Buy', 200, 410.50, 82100.00, 9.95, '2024-01-20', 'MSFT purchase'),
(3, 7, 'Buy', 20, 860.75, 17215.00, 9.95, '2024-02-01', 'NVDA purchase'),
(6, 13, 'Buy', 300, 520.40, 156120.00, 12.95, '2024-02-15', 'UNH purchase'),

-- Dividend transactions
(1, 1, 'Dividend', 1500, 0.24, 360.00, 0.00, '2024-02-15', 'AAPL dividend'),
(1, 2, 'Dividend', 800, 0.75, 600.00, 0.00, '2024-03-15', 'MSFT dividend'),
(4, 12, 'Dividend', 1000, 1.13, 1130.00, 0.00, '2024-03-20', 'JNJ dividend'),
(7, 8, 'Dividend', 3500, 1.05, 3675.00, 0.00, '2024-04-15', 'JPM dividend'),

-- Recent sales
(3, 4, 'Sell', 200, 148.90, 29780.00, 12.95, '2024-03-10', 'AMZN partial sale'),
(6, 1, 'Sell', 300, 178.20, 53460.00, 12.95, '2024-04-05', 'AAPL profit taking'),

-- Cash deposits
(1, NULL, 'Deposit', NULL, NULL, 25000.00, 0.00, '2024-01-01', 'Annual contribution'),
(5, NULL, 'Deposit', NULL, NULL, 23000.00, 0.00, '2024-01-01', '401k contribution'),
(7, NULL, 'Deposit', NULL, NULL, 100000.00, 0.00, '2024-02-01', 'Trust funding'),

-- Fees
(1, NULL, 'Fee', NULL, NULL, 150.00, 0.00, '2024-03-31', 'Quarterly management fee'),
(3, NULL, 'Fee', NULL, NULL, 250.00, 0.00, '2024-03-31', 'Quarterly management fee'),
(7, NULL, 'Fee', NULL, NULL, 400.00, 0.00, '2024-03-31', 'Quarterly management fee');

-- Insert sample performance data (last 90 days)
INSERT INTO portfolio_performance (portfolio_id, performance_date, total_value, daily_return, cumulative_return) VALUES
-- Portfolio 1 performance
(1, '2024-01-01', 1200000.00, 0.0000, 0.0000),
(1, '2024-01-31', 1220000.00, 0.0050, 0.0167),
(1, '2024-02-29', 1235000.00, 0.0025, 0.0292),
(1, '2024-03-31', 1245000.00, 0.0080, 0.0375),
(1, '2024-04-30', 1250000.00, 0.0040, 0.0417),

-- Portfolio 3 performance  
(3, '2024-01-01', 2000000.00, 0.0000, 0.0000),
(3, '2024-01-31', 2050000.00, 0.0075, 0.0250),
(3, '2024-02-29', 2080000.00, 0.0120, 0.0400),
(3, '2024-03-31', 2095000.00, 0.0065, 0.0475),
(3, '2024-04-30', 2100000.00, 0.0025, 0.0500),

-- Portfolio 7 performance
(7, '2024-01-01', 3000000.00, 0.0000, 0.0000),
(7, '2024-01-31', 3100000.00, 0.0085, 0.0333),
(7, '2024-02-29', 3150000.00, 0.0095, 0.0500),
(7, '2024-03-31', 3180000.00, 0.0070, 0.0600),
(7, '2024-04-30', 3200000.00, 0.0063, 0.0667);

-- Insert recent market data for key securities
INSERT INTO market_data (security_id, price_date, open_price, high_price, low_price, close_price, volume) VALUES
-- AAPL recent data
(1, '2024-06-25', 174.20, 176.80, 173.90, 175.43, 52340000),
(1, '2024-06-24', 172.80, 175.20, 172.10, 174.30, 48920000),
(1, '2024-06-21', 171.50, 173.40, 170.80, 172.90, 45680000),

-- MSFT recent data  
(2, '2024-06-25', 412.50, 418.90, 411.20, 415.26, 23450000),
(2, '2024-06-24', 408.70, 414.30, 407.90, 412.80, 21230000),
(2, '2024-06-21', 405.20, 410.60, 404.50, 408.90, 19870000),

-- NVDA recent data
(7, '2024-06-25', 870.40, 882.30, 868.90, 875.28, 41230000),
(7, '2024-06-24', 865.20, 875.60, 862.10, 870.50, 39840000),
(7, '2024-06-21', 860.80, 868.90, 857.30, 865.40, 37560000);

-- Update portfolio total values based on current holdings
UPDATE portfolios p SET total_value = (
    SELECT COALESCE(SUM(ph.current_value), 0) + p.cash_balance
    FROM portfolio_holdings ph 
    WHERE ph.portfolio_id = p.portfolio_id
);

-- Show some summary statistics
SELECT 'Database populated successfully!' as Status;

SELECT COUNT(*) as Total_Clients FROM clients;
SELECT COUNT(*) as Total_Portfolios FROM portfolios;
SELECT COUNT(*) as Total_Securities FROM securities;
SELECT COUNT(*) as Total_Holdings FROM portfolio_holdings;
SELECT COUNT(*) as Total_Transactions FROM transactions;

-- Show top 5 portfolios by value
SELECT 
    c.name,
    p.portfolio_name,
    p.total_value,
    p.cash_balance
FROM portfolios p
JOIN clients c ON p.client_id = c.client_id
ORDER BY p.total_value DESC
LIMIT 5; 