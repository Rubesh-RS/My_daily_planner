from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
import os

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///planner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database models
class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False)
    top_priorities = db.Column(db.Text, nullable=True)
    calls_mails = db.Column(db.Text, nullable=True)
    personal_tasks = db.Column(db.Text, nullable=True)
    todo_list = db.Column(db.Text, nullable=True)
    daily_habits = db.Column(db.Text, nullable=True)

# Ensure database exists
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    quote = "Stay positive, work hard, make it happen."  # Example quote
    return render_template('index.html', quote=quote)

@app.route('/fill-plan', methods=['GET', 'POST'])
def fill_plan():
    today = date.today()
    plan = Plan.query.filter_by(date=today).first()

    if request.method == 'POST':
        if not plan:
            plan = Plan(date=today)
            db.session.add(plan)
        plan.top_priorities = request.form.get('top_priorities', '')
        plan.calls_mails = request.form.get('calls_mails', '')
        plan.personal_tasks = request.form.get('personal_tasks', '')
        plan.todo_list = request.form.get('todo_list', '')
        plan.daily_habits = request.form.get('daily_habits', '')
        db.session.commit()
        return redirect(url_for('complete_plan'))

    return render_template('fill_plan.html', plan=plan)

@app.route('/complete-plan', methods=['GET', 'POST'])
def complete_plan():
    today = date.today()
    plan = Plan.query.filter_by(date=today).first()
    if not plan:
        return redirect(url_for('fill_plan'))

    sections = {field: getattr(plan, field).splitlines() for field in [
        'top_priorities', 'calls_mails', 'personal_tasks', 'todo_list', 'daily_habits'] if getattr(plan, field)}
    total_items = sum(len(items) for items in sections.values())

    if request.method == 'POST':
        checked_items = request.json.get('checked_items', [])
        stars = 5 * len(checked_items) / total_items if total_items > 0 else 0

        # Save data to Excel
        file_path = 'plans.xlsx'
        if not os.path.exists(file_path):
            df = pd.DataFrame(columns=['Date', 'Stars'])
        else:
            df = pd.read_excel(file_path)

        # Update the existing entry for today or add a new one
        today_str = str(today)
        if today_str in df['Date'].astype(str).values:
            df.loc[df['Date'].astype(str) == today_str, 'Stars'] = stars
        else:
            new_entry = pd.DataFrame({'Date': [today], 'Stars': [stars]})
            df = pd.concat([df, new_entry], ignore_index=True)

        # Save the updated DataFrame back to Excel
        df.to_excel(file_path, index=False)

        return jsonify({'stars': round(stars, 2)})

    return render_template('complete_plan.html', sections=sections, total_items=total_items)

@app.route('/report')
def report():
    file_path = 'plans.xlsx'
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        df['Date'] = pd.to_datetime(df['Date']).dt.date
    else:
        df = pd.DataFrame(columns=['Date', 'Stars'])

    # Create graph
    plt.figure(figsize=(10, 6))
    plt.plot(df['Date'], df['Stars'], marker='o', linestyle='-', color='b', label='Stars Earned')
    plt.xlabel('Date')
    plt.ylabel('Stars')
    plt.title('Performance Over Time')
    plt.grid(True)
    plt.legend()
    graph_path = 'static/graph.png'
    plt.savefig(graph_path)
    plt.close()

    return render_template('report.html', graph_path=graph_path)

if __name__ == '__main__':
    app.run(debug=True)
