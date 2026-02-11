# app.py
import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

# Make Matplotlib work on servers without a display
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Import evaluator
from evaluate import evaluate_answer_sheet

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
GRAPH_FOLDER = 'static/graphs'

# Create needed folders if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(GRAPH_FOLDER, exist_ok=True)

# ---------- DATABASE INITIALIZATION ----------
def init_db():
    conn = sqlite3.connect('results.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    roll_no TEXT,
                    semester TEXT,
                    marks REAL,
                    date TEXT
                )''')
    conn.commit()
    conn.close()

init_db()  # Run once to ensure table exists

# ---------- HOME PAGE ----------
@app.route('/')
def home():
    return render_template('index.html')

# ---------- UPLOAD + EVALUATE ----------
@app.route('/evaluate', methods=['POST'])
def evaluate():
    name = request.form.get('name', '').strip()
    roll_no = request.form.get('roll_no', '').strip()
    semester = request.form.get('semester', '').strip()
    file = request.files.get('file')

    if not file or file.filename == '':
        return "File upload failed!", 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Evaluate image
    marks = evaluate_answer_sheet(filepath)

    # Save to database
    conn = sqlite3.connect('results.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO results (name, roll_no, semester, marks, date) VALUES (?, ?, ?, ?, ?)",
        (name, roll_no, semester, marks, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

    # Redirect to results page
    return redirect(url_for('results'))

# ---------- RESULTS PAGE ----------
@app.route('/results')
def results():
    conn = sqlite3.connect('results.db')
    c = conn.cursor()
    c.execute("SELECT * FROM results ORDER BY id DESC")
    data = c.fetchall()
    conn.close()
    return render_template('results.html', data=data)

# ---------- GRAPH PAGE ----------
@app.route('/graph')
def graph():
    conn = sqlite3.connect('results.db')
    c = conn.cursor()
    c.execute("SELECT name        , marks FROM results ORDER BY id ASC")
    data = c.fetchall()
    conn.close()

    if not data:
        return render_template('graph.html', graph=None)

    rolls = [row[0] for row in data]
    marks = [row[1] for row in data]

    # Create bar chart
    plt.figure(figsize=(7, 4))
    plt.bar(rolls, marks)
    plt.xlabel('STUDENT NAME')
    plt.ylabel('Marks')
    plt.title('Student Performance')
    plt.tight_layout()

    graph_path = os.path.join(GRAPH_FOLDER, 'performance.png')
    plt.savefig(graph_path)
    plt.close()

    return render_template('graph.html', graph=graph_path)

# ---------- MAIN ----------
if __name__ == '__main__':
    app.run(debug=True)
