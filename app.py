from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, User, Income, Expense, SavingsGoal
from datetime import datetime
from sqlalchemy import func
import calendar

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.secret_key = 'supersecretkey'
db.init_app(app)

@app.route("/") 
def index(): 
    return redirect(url_for('dashboard'))

@app.route('/login',methods=['GET', 'POST'])
def login(): 
         if request.method == 'POST':
           return redirect(url_for('dashboard')) 
         return render_template('login.html')


@app.route('/analysis',methods=['GET', 'POST'])
def analysis(): 
         if request.method == 'POST':
           return redirect(url_for('dashboard')) 
         return render_template('analysis.html')


@app.route('/add_income', methods=['GET', 'POST'])
def add_income():
    if request.method == 'POST':
        try:
            amount = request.form['amount']
            description = request.form['description']
            date = datetime.strptime(request.form['date'], '%Y-%m-%d')
            month = calendar.month_name[date.month]

            # Assuming user_id=1 is a placeholder. Ensure user_id is handled properly.
            income = Income(amount=amount, description=description, date=date, month=month, user_id=1)
            db.session.add(income)
            db.session.commit()
            flash('Income added successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            # Log the error message for debugging
            app.logger.error(f"Error adding income: {e}")
            flash('An error occurred while adding income. Please try again.', 'danger')
            return redirect(url_for('add_income'))
    return render_template('add_income.html')

@app.route('/update_income/<int:id>', methods=['GET', 'POST'])
def update_income(id):
    income = Income.query.get(id)
    if request.method == 'POST':
        income.amount = request.form['amount']
        income.description = request.form['description']
        income.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        income.month = calendar.month_name[income.date.month]
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('update_income.html', income=income)

@app.route('/delete_income/<int:id>')
def delete_income(id):
    income = Income.query.get(id)
    db.session.delete(income)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        amount = request.form['amount']
        description = request.form['description']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        month = calendar.month_name[date.month]
        expense = Expense(amount=amount, description=description, date=date, month=month, user_id=1)
        db.session.add(expense)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('add_expense.html')

@app.route('/update_expense/<int:id>', methods=['GET', 'POST'])
def update_expense(id):
    expense = Expense.query.get(id)
    if request.method == 'POST':
        expense.amount = request.form['amount']
        expense.description = request.form['description']
        expense.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        expense.month = calendar.month_name[expense.date.month]
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('update_expense.html', expense=expense)

@app.route('/delete_expense/<int:id>')
def delete_expense(id):
    expense = Expense.query.get(id)
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/add_savings_goal', methods=['GET', 'POST'])
def add_savings_goal():
    if request.method == 'POST':
        try:
            print("Form data:", request.form)  # Debugging print statement
            target_amount = request.form['target_amount']
            description = request.form['description']
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
            due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d')
            month = calendar.month_name[start_date.month]
            goal = SavingsGoal(target_amount=target_amount, description=description, start_date=start_date, due_date=due_date, month=month, user_id=1)
            db.session.add(goal)
            db.session.commit()
            return redirect(url_for('dashboard'))
        except KeyError as e:
            print(f"Missing form field: {e}")
            flash(f"Error: Missing form field {e}", "danger")
        except Exception as e:
            print(f"An error occurred: {e}")
            flash(f"Error: {e}", "danger")
    return render_template('add_savings_goal.html')

@app.route('/update_savings_goal/<int:id>', methods=['GET', 'POST'])
def update_savings_goal(id):
    goal = SavingsGoal.query.get(id)
    if request.method == 'POST':
        try:
            print("Form data:", request.form)  # Debugging print statement
            goal.target_amount = request.form['target_amount']
            goal.description = request.form['description']
            goal.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
            goal.due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d')
            goal.month = calendar.month_name[goal.start_date.month]
            db.session.commit()
            return redirect(url_for('dashboard'))
        except KeyError as e:
            print(f"Missing form field: {e}")
            flash(f"Error: Missing form field {e}", "danger")
        except Exception as e:
            print(f"An error occurred: {e}")
            flash(f"Error: {e}", "danger")
    return render_template('update_savings_goal.html', goal=goal)

@app.route('/delete_savings_goal/<int:id>')
def delete_savings_goal(id):
    goal = SavingsGoal.query.get(id)
    db.session.delete(goal)
    db.session.commit()
    return redirect(url_for('dashboard'))

def calculate_monthly_savings(target_amount, due_date, total_income, total_expense):
    months_remaining = ((due_date.year - datetime.now().year) * 12 + due_date.month - datetime.now().month) or 1
    available_savings = total_income - total_expense
    recommended_monthly_savings = max((target_amount - available_savings) / months_remaining, 0)
    return recommended_monthly_savings

@app.route('/dashboard')
def dashboard():
    incomes = Income.query.all()
    expenses = Expense.query.all()
    goals = SavingsGoal.query.all()
    
    total_income = db.session.query(func.sum(Income.amount)).scalar() or 0
    total_expense = db.session.query(func.sum(Expense.amount)).scalar() or 0
    balance = total_income - total_expense
    
    for goal in goals:
        goal.recommended_monthly_savings = calculate_monthly_savings(goal.target_amount, goal.due_date, total_income, total_expense)
    
    recommendation_message = None
    if goals:
        if balance < max(goal.recommended_monthly_savings for goal in goals):
            recommendation_message = "Consider increasing your income, extending your goal date, or decreasing your expenses."
    else:
        recommendation_message = "No savings goals set."

    return render_template('dashboard.html', incomes=incomes, expenses=expenses, goals=goals, total_income=total_income, total_expense=total_expense, balance=balance, recommendation_message=recommendation_message)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
