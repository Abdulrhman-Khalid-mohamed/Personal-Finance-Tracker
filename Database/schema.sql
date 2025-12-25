-- Finance Tracker Database Schema

-- Create categories table
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('income', 'expense')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, type)
);

-- Create transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
    type VARCHAR(20) NOT NULL CHECK (type IN ('income', 'expense')),
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    description TEXT,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category_id);

-- Insert default categories
INSERT INTO categories (name, type) VALUES
    ('Salary', 'income'),
    ('Freelance', 'income'),
    ('Investment', 'income'),
    ('Other Income', 'income'),
    ('Food & Dining', 'expense'),
    ('Transportation', 'expense'),
    ('Utilities', 'expense'),
    ('Entertainment', 'expense'),
    ('Healthcare', 'expense'),
    ('Shopping', 'expense'),
    ('Education', 'expense'),
    ('Other Expense', 'expense')
ON CONFLICT (name, type) DO NOTHING;

-- Create a view for monthly summaries
CREATE OR REPLACE VIEW monthly_summary AS
SELECT 
    DATE_TRUNC('month', date) as month,
    type,
    SUM(amount) as total_amount,
    COUNT(*) as transaction_count
FROM transactions
GROUP BY DATE_TRUNC('month', date), type
ORDER BY month DESC, type;

-- Create a view for category summaries
CREATE OR REPLACE VIEW category_summary AS
SELECT 
    c.name as category_name,
    c.type,
    COUNT(t.id) as transaction_count,
    COALESCE(SUM(t.amount), 0) as total_amount,
    COALESCE(AVG(t.amount), 0) as avg_amount
FROM categories c
LEFT JOIN transactions t ON c.id = t.category_id
GROUP BY c.id, c.name, c.type
ORDER BY total_amount DESC;
