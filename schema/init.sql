-- schema/init.sql
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR(36) PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for querying by account
CREATE INDEX IF NOT EXISTS idx_account_id ON transactions(account_id);

-- Index for timestamp-based queries
CREATE INDEX IF NOT EXISTS idx_timestamp ON transactions(timestamp);

-- Table for storing alerts
CREATE TABLE IF NOT EXISTS alerts (
    alert_id VARCHAR(36) PRIMARY KEY,
    transaction_id VARCHAR(36) REFERENCES transactions(transaction_id),
    alert_type VARCHAR(50) NOT NULL,
    alert_message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);