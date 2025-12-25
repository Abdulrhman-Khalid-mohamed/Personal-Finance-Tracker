from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/finance_tracker')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

CORS(app)
db = SQLAlchemy(app)

# Models
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
    transactions = db.relationship('Transaction', backref='category', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type
        }

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    description = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'type': self.type,
            'category': self.category.to_dict() if self.category else None,
            'description': self.description,
            'date': self.date.isoformat(),
            'created_at': self.created_at.isoformat()
        }

# Routes
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """Get all transactions with optional filtering"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    transaction_type = request.args.get('type')
    
    query = Transaction.query
    
    if start_date:
        query = query.filter(Transaction.date >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Transaction.date <= datetime.fromisoformat(end_date))
    if transaction_type:
        query = query.filter(Transaction.type == transaction_type)
    
    transactions = query.order_by(Transaction.date.desc()).all()
    return jsonify([t.to_dict() for t in transactions])

@app.route('/api/transactions/<int:id>', methods=['GET'])
def get_transaction(id):
    """Get a specific transaction"""
    transaction = Transaction.query.get_or_404(id)
    return jsonify(transaction.to_dict())

@app.route('/api/transactions', methods=['POST'])
def create_transaction():
    """Create a new transaction"""
    data = request.json
    
    transaction = Transaction(
        amount=data['amount'],
        type=data['type'],
        category_id=data.get('category_id'),
        description=data.get('description', ''),
        date=datetime.fromisoformat(data['date']) if 'date' in data else datetime.utcnow()
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify(transaction.to_dict()), 201

@app.route('/api/transactions/<int:id>', methods=['PUT'])
def update_transaction(id):
    """Update a transaction"""
    transaction = Transaction.query.get_or_404(id)
    data = request.json
    
    transaction.amount = data.get('amount', transaction.amount)
    transaction.type = data.get('type', transaction.type)
    transaction.category_id = data.get('category_id', transaction.category_id)
    transaction.description = data.get('description', transaction.description)
    if 'date' in data:
        transaction.date = datetime.fromisoformat(data['date'])
    
    db.session.commit()
    return jsonify(transaction.to_dict())

@app.route('/api/transactions/<int:id>', methods=['DELETE'])
def delete_transaction(id):
    """Delete a transaction"""
    transaction = Transaction.query.get_or_404(id)
    db.session.delete(transaction)
    db.session.commit()
    return jsonify({'message': 'Transaction deleted'}), 200

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    categories = Category.query.all()
    return jsonify([c.to_dict() for c in categories])

@app.route('/api/categories', methods=['POST'])
def create_category():
    """Create a new category"""
    data = request.json
    category = Category(name=data['name'], type=data['type'])
    db.session.add(category)
    db.session.commit()
    return jsonify(category.to_dict()), 201

@app.route('/api/analytics/summary', methods=['GET'])
def get_summary():
    """Get financial summary"""
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    total_income = db.session.query(db.func.sum(Transaction.amount))\
        .filter(Transaction.type == 'income').scalar() or 0
    total_expenses = db.session.query(db.func.sum(Transaction.amount))\
        .filter(Transaction.type == 'expense').scalar() or 0
    
    monthly_income = db.session.query(db.func.sum(Transaction.amount))\
        .filter(Transaction.type == 'income', Transaction.date >= thirty_days_ago).scalar() or 0
    monthly_expenses = db.session.query(db.func.sum(Transaction.amount))\
        .filter(Transaction.type == 'expense', Transaction.date >= thirty_days_ago).scalar() or 0
    
    return jsonify({
        'total_income': float(total_income),
        'total_expenses': float(total_expenses),
        'balance': float(total_income - total_expenses),
        'monthly_income': float(monthly_income),
        'monthly_expenses': float(monthly_expenses),
        'monthly_balance': float(monthly_income - monthly_expenses)
    })

@app.route('/api/analytics/by-category', methods=['GET'])
def get_by_category():
    """Get spending/income by category"""
    results = db.session.query(
        Category.name,
        Transaction.type,
        db.func.sum(Transaction.amount).label('total')
    ).join(Transaction).group_by(Category.name, Transaction.type).all()
    
    return jsonify([{
        'category': r[0],
        'type': r[1],
        'total': float(r[2])
    } for r in results])

@app.route('/api/import/csv', methods=['POST'])
def import_csv():
    """Import transactions from CSV file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        df = pd.read_csv(file)
        required_columns = ['date', 'amount', 'type', 'category', 'description']
        
        if not all(col in df.columns for col in required_columns):
            return jsonify({'error': 'Missing required columns'}), 400
        
        imported_count = 0
        for _, row in df.iterrows():
            # Find or create category
            category = Category.query.filter_by(name=row['category'], type=row['type']).first()
            if not category:
                category = Category(name=row['category'], type=row['type'])
                db.session.add(category)
                db.session.flush()
            
            transaction = Transaction(
                amount=float(row['amount']),
                type=row['type'],
                category_id=category.id,
                description=row['description'],
                date=pd.to_datetime(row['date']).date()
            )
            db.session.add(transaction)
            imported_count += 1
        
        db.session.commit()
        return jsonify({'message': f'Successfully imported {imported_count} transactions'}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    """Export transactions to CSV file"""
    transactions = Transaction.query.all()
    
    data = [{
        'date': t.date.isoformat(),
        'amount': t.amount,
        'type': t.type,
        'category': t.category.name if t.category else '',
        'description': t.description
    } for t in transactions]
    
    df = pd.DataFrame(data)
    
    export_path = 'data/exports/transactions_export.csv'
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    df.to_csv(export_path, index=False)
    
    return send_file(export_path, as_attachment=True, download_name='transactions.csv')

@app.route('/')
def index():
    return jsonify({'message': 'Finance Tracker API', 'version': '1.0'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create default categories if they don't exist
        if Category.query.count() == 0:
            default_categories = [
                Category(name='Salary', type='income'),
                Category(name='Freelance', type='income'),
                Category(name='Food', type='expense'),
                Category(name='Transportation', type='expense'),
                Category(name='Utilities', type='expense'),
                Category(name='Entertainment', type='expense'),
                Category(name='Healthcare', type='expense'),
            ]
            db.session.add_all(default_categories)
            db.session.commit()
    
    app.run(debug=True, port=5000)
