const API_URL = 'http://localhost:5000/api';

let categoryChart = null;
let categories = [];

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadCategories();
    loadTransactions();
    loadSummary();
    loadCategoryChart();
    setupEventListeners();
    setDefaultDate();
});

function setDefaultDate() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('date').value = today;
}

function setupEventListeners() {
    document.getElementById('transactionForm').addEventListener('submit', handleAddTransaction);
    document.getElementById('type').addEventListener('change', handleTypeChange);
    document.getElementById('csvFile').addEventListener('change', handleFileImport);
    document.getElementById('exportBtn').addEventListener('click', handleExport);
    document.getElementById('applyFilter').addEventListener('click', applyFilter);
}

// Load categories
async function loadCategories() {
    try {
        const response = await fetch(`${API_URL}/categories`);
        categories = await response.json();
        updateCategoryDropdown();
    } catch (error) {
        console.error('Error loading categories:', error);
        showNotification('Error loading categories', 'error');
    }
}

function updateCategoryDropdown() {
    const type = document.getElementById('type').value;
    const categorySelect = document.getElementById('category');
    
    const filteredCategories = categories.filter(c => c.type === type);
    
    categorySelect.innerHTML = filteredCategories.map(c => 
        `<option value="${c.id}">${c.name}</option>`
    ).join('');
}

function handleTypeChange() {
    updateCategoryDropdown();
}

// Load transactions
async function loadTransactions(filterType = '') {
    try {
        let url = `${API_URL}/transactions`;
        if (filterType) {
            url += `?type=${filterType}`;
        }
        
        const response = await fetch(url);
        const transactions = await response.json();
        displayTransactions(transactions);
    } catch (error) {
        console.error('Error loading transactions:', error);
        showNotification('Error loading transactions', 'error');
    }
}

function displayTransactions(transactions) {
    const tbody = document.getElementById('transactionsBody');
    
    if (transactions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No transactions found</td></tr>';
        return;
    }
    
    tbody.innerHTML = transactions.map(t => `
        <tr>
            <td>${new Date(t.date).toLocaleDateString()}</td>
            <td>${t.description}</td>
            <td>${t.category ? t.category.name : 'N/A'}</td>
            <td><span class="badge ${t.type}">${t.type}</span></td>
            <td class="${t.type === 'income' ? 'text-success' : 'text-danger'}">
                ${t.type === 'income' ? '+' : '-'}$${t.amount.toFixed(2)}
            </td>
            <td>
                <button class="btn-delete" onclick="deleteTransaction(${t.id})">Delete</button>
            </td>
        </tr>
    `).join('');
}

// Load summary
async function loadSummary() {
    try {
        const response = await fetch(`${API_URL}/analytics/summary`);
        const summary = await response.json();
        
        document.getElementById('totalIncome').textContent = `$${summary.total_income.toFixed(2)}`;
        document.getElementById('totalExpenses').textContent = `$${summary.total_expenses.toFixed(2)}`;
        document.getElementById('balance').textContent = `$${summary.balance.toFixed(2)}`;
    } catch (error) {
        console.error('Error loading summary:', error);
        showNotification('Error loading summary', 'error');
    }
}

// Load category chart
async function loadCategoryChart() {
    try {
        const response = await fetch(`${API_URL}/analytics/by-category`);
        const data = await response.json();
        
        const expenses = data.filter(d => d.type === 'expense');
        
        const ctx = document.getElementById('categoryChart').getContext('2d');
        
        if (categoryChart) {
            categoryChart.destroy();
        }
        
        categoryChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: expenses.map(e => e.category),
                datasets: [{
                    label: 'Expenses by Category',
                    data: expenses.map(e => e.total),
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56',
                        '#4BC0C0',
                        '#9966FF',
                        '#FF9F40',
                        '#FF6384',
                        '#C9CBCF'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: false
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading chart:', error);
    }
}

// Add transaction
async function handleAddTransaction(e) {
    e.preventDefault();
    
    const formData = {
        amount: parseFloat(document.getElementById('amount').value),
        type: document.getElementById('type').value,
        category_id: parseInt(document.getElementById('category').value),
        description: document.getElementById('description').value,
        date: document.getElementById('date').value
    };
    
    try {
        const response = await fetch(`${API_URL}/transactions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            showNotification('Transaction added successfully!', 'success');
            document.getElementById('transactionForm').reset();
            setDefaultDate();
            loadTransactions();
            loadSummary();
            loadCategoryChart();
        } else {
            throw new Error('Failed to add transaction');
        }
    } catch (error) {
        console.error('Error adding transaction:', error);
        showNotification('Error adding transaction', 'error');
    }
}

// Delete transaction
async function deleteTransaction(id) {
    if (!confirm('Are you sure you want to delete this transaction?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/transactions/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification('Transaction deleted successfully!', 'success');
            loadTransactions();
            loadSummary();
            loadCategoryChart();
        } else {
            throw new Error('Failed to delete transaction');
        }
    } catch (error) {
        console.error('Error deleting transaction:', error);
        showNotification('Error deleting transaction', 'error');
    }
}

// Import CSV
async function handleFileImport(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_URL}/import/csv`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showNotification(result.message, 'success');
            loadTransactions();
            loadSummary();
            loadCategoryChart();
        } else {
            throw new Error(result.error || 'Import failed');
        }
    } catch (error) {
        console.error('Error importing CSV:', error);
        showNotification('Error importing CSV: ' + error.message, 'error');
    }
    
    e.target.value = '';
}

// Export CSV
async function handleExport() {
    try {
        const response = await fetch(`${API_URL}/export/csv`);
        const blob = await response.blob();
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'transactions.csv';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showNotification('Transactions exported successfully!', 'success');
    } catch (error) {
        console.error('Error exporting CSV:', error);
        showNotification('Error exporting transactions', 'error');
    }
}

// Apply filter
function applyFilter() {
    const filterType = document.getElementById('filterType').value;
    loadTransactions(filterType);
}

// Show notification
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'success' ? '#4caf50' : '#f44336'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}
