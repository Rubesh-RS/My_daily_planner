from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use Agg backend for non-GUI usage
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
    QUOTES = "Believe in yourself and all that you are.", "Your limitation—it's only your imagination.", "Push yourself, because no one else is going to do it for you.", "Great things never come from comfort zones.", "Dream it. Wish it. Do it.", "Success doesn’t just find you. You have to go out and get it.", "The harder you work for something, the greater you’ll feel when you achieve it.", "Dream bigger. Do bigger.", "Don’t stop when you’re tired. Stop when you’re done.", "Wake up with determination. Go to bed with satisfaction.", "Do something today that your future self will thank you for.", "Little things make big days.", "It’s going to be hard, but hard does not mean impossible.", "Don’t wait for opportunity. Create it.", "Sometimes we’re tested not to show our weaknesses, but to discover our strengths.", "The key to success is to focus on goals, not obstacles.", "Dream it. Believe it. Build it.", "Action is the foundational key to all success.", "Failure is not the opposite of success; it’s part of success.", "The best way to predict the future is to create it.", "Don’t watch the clock; do what it does. Keep going.", "You are capable of amazing things.", "Doubt kills more dreams than failure ever will.", "A goal without a plan is just a wish.", "Work hard in silence, let success make the noise.", "Keep going because you did not come this far just to come this far.", "The secret to getting ahead is getting started.", "Believe you can and you’re halfway there.", "Nothing is impossible. The word itself says ‘I’m possible!’", "Life is 10% what happens to us and 90% how we react to it.", "Fall seven times, stand up eight.", "Your passion is waiting for your courage to catch up.", "Success is not for the lazy.", "Your attitude determines your direction.", "Don’t be afraid to give up the good to go for the great.", "A little progress each day adds up to big results.", "Stay positive, work hard, make it happen.", "Be so good they can’t ignore you.", "Opportunities don't happen. You create them.", "Success usually comes to those who are too busy to be looking for it.", "Don’t be pushed around by the fears in your mind. Be led by the dreams in your heart.", "Hustle beats talent when talent doesn’t hustle.", "Don’t let yesterday take up too much of today.", "You don’t have to be great to start, but you have to start to be great.", "Act as if what you do makes a difference. It does.", "What you get by achieving your goals is not as important as what you become by achieving your goals.", "Hardships often prepare ordinary people for an extraordinary destiny.", "Success is the sum of small efforts repeated day in and day out.", "Success is liking yourself, liking what you do, and liking how you do it.", "Start where you are. Use what you have. Do what you can.", "If you’re going through hell, keep going.", "The future depends on what you do today.", "You only fail when you stop trying.", "It always seems impossible until it’s done.", "Quality is not an act, it is a habit.", "Don’t be afraid to fail. Be afraid not to try.", "Everything you’ve ever wanted is on the other side of fear.", "Discipline is the bridge between goals and accomplishment.", "You don’t have to see the whole staircase, just take the first step.", "A winner is a dreamer who never gives up.", "The only limit to our realization of tomorrow will be our doubts of today.", "Happiness is not something ready-made. It comes from your own actions.", "Do what you can with all you have, wherever you are.", "Your best teacher is your last mistake.", "We generate fears while we sit. We overcome them by action.", "Success is the best revenge.", "The only way to achieve the impossible is to believe it is possible.", "Small steps in the right direction can turn out to be the biggest step of your life.", "Be the change that you wish to see in the world.", "Perseverance is not a long race; it is many short races one after the other.", "Success is how high you bounce when you hit bottom.", "The best way out is always through.", "Failure is simply the opportunity to begin again, this time more intelligently.", "Work until your idols become your rivals.", "The harder the struggle, the more glorious the triumph.", "Strive not to be a success, but rather to be of value.", "Don’t limit your challenges; challenge your limits.", "Motivation gets you started. Habit keeps you going.", "If opportunity doesn’t knock, build a door.", "Winners are not people who never fail but people who never quit.", "Success is not in what you have, but who you are.", "The journey of a thousand miles begins with a single step.", "If you believe in yourself, anything is possible.", "It’s not whether you get knocked down, it’s whether you get up.", "Dreams don’t work unless you do.", "Do the best you can until you know better. Then when you know better, do better.", "If you can dream it, you can do it.", "Challenges are what make life interesting, and overcoming them is what makes life meaningful.", "Life is short. Do stuff that matters.", "Don’t let what you cannot do interfere with what you can do.", "Even if you’re on the right track, you’ll get run over if you just sit there.", "Courage doesn’t always roar. Sometimes courage is the quiet voice at the end of the day saying, ‘I will try again tomorrow.’"
    quote = QUOTES[date.today().day % len(QUOTES)]  # Example quote
    return render_template('index.html', quote=quote)

@app.route('/fill_later')
def fill_later():
    return render_template('fill_later.html')

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

    return render_template('fill_plan.html', plan=plan, date=today)

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
