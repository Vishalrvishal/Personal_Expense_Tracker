from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Vishal@2004'
app.config['MYSQL_DB'] = 'expense_tracker'

mysql = MySQL(app)

# Home Page - Dashboard
@app.route('/')
def index():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Get all expenses
    cursor.execute("SELECT * FROM expenses")
    expenses = cursor.fetchall()

    # Calculate total expenses
    total = sum(float(exp['amount']) for exp in expenses)

    # Get limit
    cursor.execute("SELECT spending_limit FROM settings WHERE id = 1")
    limit_result = cursor.fetchone()
    spending_limit = limit_result['spending_limit'] if limit_result else 0.0

    over_limit = total > spending_limit and spending_limit != 0

    return render_template("dashboard.html", expenses=expenses, total=total, spending_limit=spending_limit, over_limit=over_limit)

# Add Expense
@app.route('/add', methods=['POST'])
def add_expense():
    if request.method == 'POST':
        date = request.form['date']
        category = request.form['category']
        description = request.form['description']
        amount = request.form['amount']

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO expenses (date, category, description, amount) VALUES (%s, %s, %s, %s)",
                       (date, category, description, amount))
        mysql.connection.commit()
        flash("Expense added successfully!")
        return redirect(url_for('index'))

# Delete Expense
@app.route('/delete/<int:id>')
def delete_expense(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = %s", (id,))
    mysql.connection.commit()
    flash("Expense deleted successfully!")
    return redirect(url_for('index'))

# Edit Expense
@app.route('/edit/<int:id>', methods=['POST'])
def edit_expense(id):
    if request.method == 'POST':
        date = request.form['date']
        category = request.form['category']
        description = request.form['description']
        amount = request.form['amount']

        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE expenses 
            SET date=%s, category=%s, description=%s, amount=%s 
            WHERE id=%s
        """, (date, category, description, amount, id))
        mysql.connection.commit()
        flash("Expense updated successfully!")
        return redirect(url_for('index'))

# Set Limit
@app.route('/set_limit', methods=['POST'])
def set_limit():
    new_limit = request.form['limit']
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE settings SET spending_limit = %s WHERE id = 1", (new_limit,))
    mysql.connection.commit()
    flash("Spending limit updated!")
    return redirect(url_for('index'))

# Reset
@app.route('/reset', methods=['POST'])
def reset():
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM expenses")
    cursor.execute("UPDATE settings SET spending_limit = 0 WHERE id = 1")
    mysql.connection.commit()
    flash("Expenses and limit reset!")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
