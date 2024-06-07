from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flashcards.db'
db = SQLAlchemy(app)

# Function to get all table names
def get_table_names():
    with db.engine.connect() as conn:
        tables = conn.execute(db.text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
    return [table[0] for table in tables]

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
    INSERT INTO {table_name} (question, explanation) VALUES (:question, :explanation)
    """
    db.session.execute(db.text(add_question_sql), {'question': question, 'explanation': explanation})
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/admin/delete_table', methods=['POST'])
def delete_table():
    table_name = request.form['table_name']
    delete_table_sql = f"DROP TABLE IF EXISTS {table_name}"
    db.session.execute(db.text(delete_table_sql))
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/admin/view_tables', methods=['POST'])
def view_tables():
    tables = get_table_names()
    return render_template('view_tables.html', tables=tables)

@app.route('/admin/view_questions/<string:table_name>', methods=['GET'])
def view_questions(table_name):
    view_questions_sql = f"SELECT id, question, explanation FROM {table_name}"
    questions = db.session.execute(db.text(view_questions_sql)).fetchall()
    return render_template('view_questions.html', table_name=table_name, questions=questions)

@app.route('/admin/update_question/<string:table_name>/<int:question_id>', methods=['POST'])
def update_question(table_name, question_id):
    question = request.form['question']
    explanation = request.form['explanation']
    update_question_sql = f"""
    UPDATE {table_name} SET question = :question, explanation = :explanation WHERE id = :id
    """
    db.session.execute(db.text(update_question_sql), {'question': question, 'explanation': explanation, 'id': question_id})
    db.session.commit()
    return redirect(url_for('view_questions', table_name=table_name))

@app.route('/admin/delete_question/<string:table_name>/<int:question_id>', methods=['POST'])
def delete_question(table_name, question_id):
    delete_question_sql = f"DELETE FROM {table_name} WHERE id = :id"
    db.session.execute(db.text(delete_question_sql), {'id': question_id})
    db.session.commit()
    return redirect(url_for('view_questions', table_name=table_name))

if __name__ == '__main__':
    app.run(debug=True)
