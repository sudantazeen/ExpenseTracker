from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from datetime import date
import plotly.graph_objs as go
import matplotlib.pyplot as plt
from collections import defaultdict
import io
import base64

app = Flask(__name__)
db_name = "expense_tracker.db"
income_db_name = "income_tracker.db"
budget_db_name = "budget_tracker.db"

# ------------------ Expense Tracker Routes ------------------

@app.route('/')
def index():
    # Fetch and display expense records
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses")
    records = cursor.fetchall()
    conn.close()
    return render_template('index.html', records=records)

@app.route('/save', methods=['POST'])


def save_record():
    # Save a new expense record
    item_name = request.form['item_name']
    item_cost = int(request.form['item_cost'])
    category = request.form['category']
    mode_of_payment = request.form['mode_of_payment']
    purchase_date = request.form['purchase_date']

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (item_name, item_cost, category, mode_of_payment, purchase_date) VALUES (?, ?, ?, ?, ?)",
        (item_name, item_cost, category, mode_of_payment, purchase_date))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

# ... (Additional routes for updating and deleting expense records)

@app.route('/get_records')
def get_records():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses")
    records = cursor.fetchall()
    conn.close()

    records_list = []
    for record in records:
        record_dict = {
            "id": record[0],  # Add the ID to the dictionary
            "item_name": record[1],
            "item_cost": record[2],
            "category": record[3],
            "mode_of_payment": record[4],
            "purchase_date": record[5]
        }
        records_list.append(record_dict)

    return jsonify(records_list)  # Return the records as JSON


@app.route('/delete/<int:record_id>', methods=['POST'])
def delete_record(record_id):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id=?", (record_id,))
    conn.commit()
    conn.close()

    return 'Record deleted successfully', 200  # Return a success status code

# Route for Update the records

@app.route('/update/<int:record_id>', methods=['POST'])
def update_record(record_id):
    data = request.json

    item_name = data['item_name']
    item_cost = int(data['item_cost'])
    category = data['category']
    mode_of_payment = data['mode_of_payment']
    purchase_date = data['purchase_date']

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("UPDATE expenses SET item_name=?, item_cost=?, category=?, mode_of_payment=?, purchase_date=? WHERE id=?",
                   (item_name, item_cost, category, mode_of_payment, purchase_date, record_id))
    conn.commit()
    conn.close()

    return 'Record updated successfully', 200


# ------------------ Income Tracker Routes ------------------

#Route for Displaying the Income Records

@app.route('/income')
def income():
    conn = sqlite3.connect(income_db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM income_records")
    income_records = cursor.fetchall()  # Use correct variable name here
    conn.close()
    return render_template('income.html', income_records=income_records)  # Use correct variable name here

#Route for displaying saving income

@app.route('/save_income', methods=['POST'])
def save_income_record():
    source_of_income = request.form['source_of_income']
    amount = int(request.form['amount'])  # Convert to float (or int) depending on your use case
    income_date = request.form['income_date']

    conn = sqlite3.connect(income_db_name)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO income_records (source_of_income, amount, income_date) VALUES (?, ?, ?)",
        (source_of_income, amount, income_date))
    conn.commit()
    conn.close()

    return redirect(url_for('income'))  # Redirect to the income route

# Route for delete income record

@app.route('/delete_income/<int:record_id>', methods=['POST'])
def delete_income_record(record_id):
    conn = sqlite3.connect(income_db_name)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM income_records WHERE id=?", (record_id,))
    conn.commit()
    conn.close()

    return 'Income record deleted successfully', 200
#Update Income record

@app.route('/update_income/<int:record_id>', methods=['POST'])
def update_income_record(record_id):
    data = request.json

    source_of_income = data['source_of_income']
    income_date = data['income_date']

    conn = sqlite3.connect(income_db_name)
    cursor = conn.cursor()
    cursor.execute("UPDATE income_records SET source_of_income=?, income_date=? WHERE id=?",
                   (source_of_income, income_date, record_id))
    conn.commit()
    conn.close()

    return 'Income record updated successfully', 200

# Route to render the Budget Tracker page
@app.route('/budget')
def budget():
    conn = sqlite3.connect(budget_db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM budget_records")
    budget_records = cursor.fetchall()
    conn.close()
    return render_template('budget.html', budget_records=budget_records)

# Route to get budget records
@app.route('/get_budget_records')
def get_budget_records():
    conn = sqlite3.connect(budget_db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM budget_records")
    budget_records = cursor.fetchall()
    conn.close()

    records_list = []
    for record in budget_records:
        record_dict = {
            "id": record[0],
            "category": record[1],
            "amount": record[2],
            "month": record[3]
        }
        records_list.append(record_dict)

    return jsonify(records_list)

# Route to save a budget record
@app.route('/save_budget', methods=['POST'])
def save_budget_record():
    category = request.form['category']
    amount = int(request.form['budget_amount'])
    month = request.form['month']

    conn = sqlite3.connect(budget_db_name)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO budget_records (category, amount, month) VALUES (?, ?, ?)",
        (category, amount, month))
    conn.commit()
    conn.close()

    return redirect(url_for('budget'))

# Route to update a budget record
@app.route('/update_budget/<int:record_id>', methods=['POST'])
def update_budget_record(record_id):
    data = request.json
    category = data['category']
    amount = int(data['amount'])
    month = data['month']

    conn = sqlite3.connect(budget_db_name)
    cursor = conn.cursor()
    cursor.execute("UPDATE budget_records SET category=?, amount=?, month=? WHERE id=?",
                   (category, amount, month, record_id))
    conn.commit()
    conn.close()

    return 'Budget record updated successfully', 200

# Route to delete a budget record
@app.route('/delete_budget/<int:record_id>', methods=['POST'])
def delete_budget_record(record_id):
    conn = sqlite3.connect(budget_db_name)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM budget_records WHERE id=?", (record_id,))
    conn.commit()
    conn.close()

    return 'Budget record deleted successfully', 200

#Route to insights Page

# Calculate insights

# (Calculation of total expenses, income, budget)



@app.route('/insights')
def insights():
    # Fetch data from the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses")
    expenses_records = cursor.fetchall()
    conn.close()

    conn = sqlite3.connect(income_db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM income_records")
    income_records = cursor.fetchall()
    conn.close()

    conn = sqlite3.connect(budget_db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM budget_records")
    budget_records = cursor.fetchall()
    conn.close()

    # Calculate insights (you can customize these calculations)
    total_expenses = sum(record[2] for record in expenses_records)
    total_income = sum(record[2] for record in income_records)
    total_budget = sum(record[2] for record in budget_records)

    # Create bar chart
    expense_categories = [record[3] for record in expenses_records]
    expense_amounts = [record[2] for record in expenses_records]

    bar_chart = go.Figure([go.Bar(x=expense_categories, y=expense_amounts)])
    bar_chart.update_layout(title='Expenses by Category')

    # Save bar chart as an image
    img = io.BytesIO()
    bar_chart.write_image(img, format='png')
    bar_chart_image = base64.b64encode(img.getvalue()).decode()

    # Create pie chart
    budget_categories = [record[1] for record in budget_records]
    budget_amounts = [record[2] for record in budget_records]

    plt.figure(figsize=(6, 6))
    plt.pie(budget_amounts, labels=budget_categories, autopct='%1.1f%%')
    plt.title('Budget Allocation')
    pie_chart_image = get_image_base64()

    return render_template('insights.html', total_expenses=total_expenses, total_income=total_income, total_budget=total_budget,
                           bar_chart_image=bar_chart_image, pie_chart_image=pie_chart_image)

# Helper function to convert matplotlib plot to base64 image
def get_image_base64():
    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close()
    return base64.b64encode(img.getvalue()).decode()


# ------------------ Database Initialization ------------------

# ... (Creating tables if they don't exist)

if __name__ == '__main__':
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_name TEXT,
                    item_cost INTEGER,
                    category TEXT,
                    mode_of_payment TEXT,
                    purchase_date DATE
                )''')
    conn.commit()
    conn.close()


    conn = sqlite3.connect(income_db_name)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS income_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_of_income TEXT,
                        amount INTEGER,  -- Add the 'amount' column here
                        income_date DATE
                    )''')
    conn.commit()
    conn.close()

    conn = sqlite3.connect(budget_db_name)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS budget_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT,
                        amount INTEGER,
                        month TEXT
                    )''')
    conn.commit()
    conn.close()



    app.run(debug=True)
