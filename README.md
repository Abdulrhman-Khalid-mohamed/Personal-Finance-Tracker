## 🚀 Features

- Track income and expenses with categories
- Visual dashboard with charts and statistics
- CSV import/export functionality
- RESTful API backend
- Data analysis with Pandas
- PostgreSQL database storage
- Responsive web interface

## 🛠️ Tech Stack

**Backend:**
- Python Flask (REST API)
- PostgreSQL (Database)
- Pandas (Data processing)
- SQLAlchemy (ORM)

**Frontend:**
- HTML/CSS/JavaScript
- Chart.js (Data visualization)
- Fetch API

**Tools:**
- Git/GitHub
- VS Code
- Linux

## 📁 Project Structure

```
finance-tracker/
├── backend/
│   ├── app.py                 # Flask application
│   ├── models.py              # Database models
│   ├── routes.py              # API routes
│   ├── config.py              # Configuration
│   ├── requirements.txt       # Python dependencies
│   └── data_processor.py      # Pandas data processing
├── frontend/
│   ├── index.html             # Main page
│   ├── styles.css             # Styling
│   └── app.js                 # Frontend logic
├── data/
│   ├── sample_transactions.csv
│   └── exports/
├── database/
│   └── schema.sql             # Database schema
├── .gitignore
├── README.md
└── setup.sh                   # Setup script
```

## 🔧 Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 14+ (optional, for package management)
- PostgreSQL 12+
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Abdulrhman-Khalid-mohamed/finance-tracker.git
cd finance-tracker
```

2. **Set up PostgreSQL database**
```bash
# Login to PostgreSQL
sudo -u postgres psql

# Create database
CREATE DATABASE finance_tracker;
CREATE USER finance_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE finance_tracker TO finance_user;
\q
```

3. **Initialize database schema**
```bash
psql -U finance_user -d finance_tracker -f database/schema.sql
```

4. **Install Python dependencies**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

5. **Configure environment variables**
```bash
# Create .env file in backend/
cat > .env << EOF
DATABASE_URL=postgresql://finance_user:your_password@localhost/finance_tracker
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
EOF
```

6. **Run the application**
```bash
# Backend (from backend/ directory)
python app.py

# Frontend - Open frontend/index.html in browser
# Or use Python's simple server:
cd ../frontend
python3 -m http.server 8080
```

## 📊 API Endpoints

### Transactions
- `GET /api/transactions` - Get all transactions
- `GET /api/transactions/<id>` - Get specific transaction
- `POST /api/transactions` - Create new transaction
- `PUT /api/transactions/<id>` - Update transaction
- `DELETE /api/transactions/<id>` - Delete transaction

### Categories
- `GET /api/categories` - Get all categories
- `POST /api/categories` - Create new category

### Analytics
- `GET /api/analytics/summary` - Get financial summary
- `GET /api/analytics/by-category` - Get spending by category
- `GET /api/analytics/monthly` - Get monthly trends

### Data Import/Export
- `POST /api/import/csv` - Import transactions from CSV
- `GET /api/export/csv` - Export transactions to CSV

## 💾 Database Schema

**transactions table:**
- id (PRIMARY KEY)
- amount (DECIMAL)
- type (VARCHAR) - 'income' or 'expense'
- category_id (FOREIGN KEY)
- description (TEXT)
- date (DATE)
- created_at (TIMESTAMP)

**categories table:**
- id (PRIMARY KEY)
- name (VARCHAR)
- type (VARCHAR) - 'income' or 'expense'

## 📈 Sample CSV Format

```csv
date,amount,type,category,description
2024-12-01,1500.00,income,Salary,Monthly salary
2024-12-02,50.00,expense,Food,Grocery shopping
2024-12-03,30.00,expense,Transportation,Gas
```

## 🧪 Testing

```bash
# Run backend tests
cd backend
python -m pytest tests/

# Test API endpoints
curl http://localhost:5000/api/transactions
```

## 🎯 Future Enhancements

- [ ] User authentication (JWT)
- [ ] Multi-currency support
- [ ] Budget planning and alerts
- [ ] Mobile responsive design improvements
- [ ] Data backup/restore functionality
- [ ] Advanced filtering and search
- [ ] Export to PDF reports

## 📝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 👤 Author

**Abdulrhman Khalid**
- GitHub: [@Abdulrhman-Khalid-mohamed](https://github.com/Abdulrhman-Khalid-mohamed)

## 🙏 Acknowledgments

- Flask documentation
- Chart.js for beautiful visualizations
- PostgreSQL community
