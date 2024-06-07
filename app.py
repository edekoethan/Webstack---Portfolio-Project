from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flashcards.db'
db = SQLAlchemy(app)

# Function to get all table names
def get_table_names():
    meta = MetaData()
    meta.reflect(bind=db.engine)
    return meta.tables.keys()

@app.route('/')
def home():
    return render_template('index.html')  # Ensure you have index.html

@app.route('/admin')
def admin():
    tables = get_table_names()
    return render_template('admin.html', tables=tables)

@app.route('/admin/create_table', methods=['POST'])
def create_table():
    table_name = request.form['table_name']
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        explanation TEXT NOT NULL
    )
    """
    db.session.execute(db.text(create_table_sql))
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/admin/add_question', methods=['POST'])
def add_question():
    table_name = request.form['table_name']
    question = request.form['question']
    explanation = request.form['explanation']
    add_question_sql = f"""
    INSERT INTO {table_name} (question, explanation)
    VALUES (:question, :explanation)
    """
    db.session.execute(db.text(add_question_sql), {'question': question, 'explanation': explanation})
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/admin/delete_table', methods=['POST'])
def delete_table():
    table_name = request.form['table_name']
    drop_table_sql = f"DROP TABLE IF EXISTS {table_name}"
    db.session.execute(db.text(drop_table_sql))
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/admin/view_tables', methods=['GET'])
def view_tables():
    tables = get_table_names()
    return render_template('view_tables.html', tables=tables)

@app.route('/admin/view_questions', methods=['POST'])
def view_questions():
    table_name = request.form['table_name']
    questions = db.session.execute(db.text(f"SELECT * FROM {table_name}")).fetchall()
    return render_template('view_questions.html', table_name=table_name, questions=questions)

if __name__ == '__main__':
    app.run(debug=True)
