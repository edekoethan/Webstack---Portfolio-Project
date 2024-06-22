from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flashcards.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    second_name = db.Column(db.String(150), nullable=False)
    phone_no = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# favorite model
class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    flashcard_id = db.Column(db.Integer, nullable=False)
    table_name = db.Column(db.String(150), nullable=False)
    question = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=False)

    user = db.relationship('User', backref=db.backref('favorites', lazy=True))


# Function to get all table names except for 'user' table
def get_table_names():
    with db.engine.connect() as conn:
        tables = conn.execute(db.text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT IN ('user', 'sqlite_sequence', 'user_favorite_flashcard', 'favorite', 'flashcard')")).fetchall()
    return [table[0] for table in tables]

# Function to get total number of flashcards
def get_total_flashcards():
    total_flashcards = 0
    tables = get_table_names()
    with db.engine.connect() as conn:
        for table in tables:
            count = conn.execute(db.text(f"SELECT COUNT(*) FROM {table}")).scalar()
            total_flashcards += count
    return total_flashcards

@app.route('/dashboard')
def dashboard():
    tables = get_table_names()
    total_decks = len(tables)
    total_flashcards = get_total_flashcards()
    recent_activity = session.get('recent_activity', 'None')

    # Assign random colors to each deck
    deck_colors = {table: "#{:06x}".format(random.randint(0x000000, 0xFFFFFF)) for table in tables}
    # Exclude black color
    deck_colors = {table: color if color != "#000000" else "#{:06x}".format(random.randint(0x000001, 0xFFFFFF)) for table, color in deck_colors.items()}

    return render_template('dashboard.html', tables=tables, total_decks=total_decks, total_flashcards=total_flashcards, recent_activity=recent_activity, deck_colors=deck_colors)

@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        # Process the contact form submission as needed
        flash('Thank you for your message!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('contact.html')

@app.route('/submit', methods=['POST'])
def submit_contact():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    # Process the contact form submission as needed
    return redirect(url_for('dashboard'))

@app.route('/view_flashcards/<string:table_name>')
def view_flashcards(table_name):
    session['recent_activity'] = table_name
    view_questions_sql = f"SELECT id, question, explanation FROM {table_name}"
    questions = db.session.execute(db.text(view_questions_sql)).fetchall()

    user_favorite_flashcard_ids = []
    if 'user_id' in session:
        user_id = session['user_id']
        favorites = Favorite.query.filter_by(user_id=user_id, table_name=table_name).all()
        user_favorite_flashcard_ids = [favorite.flashcard_id for favorite in favorites]

    return render_template('view_flashcards.html', table_name=table_name, questions=questions, user_favorite_flashcard_ids=user_favorite_flashcard_ids)

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

@app.route('/administrator2')
def administrator2():
    tables = get_table_names()
    return render_template('administrator2.html', tables=tables)

@app.route('/administrator2/add_question', methods=['POST'])
def add_question_admin2():
    table_name = request.form['table_name']
    question_file = request.files['question']
    explanation_file = request.files['explanation']
    question_text = request.form['question_text']
    explanation_text = request.form['explanation_text']

    # Ensure at least one type of input is provided for question and explanation
    if not (question_file or question_text) or not (explanation_file or explanation_text):
        flash('You must provide either text or a file for both question and explanation.')
        return redirect(url_for('administrator2'))

    question_filename = ''
    explanation_filename = ''

    if question_file:
        if question_file.content_length > app.config['MAX_CONTENT_PATH']:
            flash('Question file size exceeds the limit of 1 MB.')
            return redirect(url_for('administrator2'))
        question_filename = secure_filename(question_file.filename)
        question_file.save(os.path.join(app.config['UPLOAD_FOLDER'], question_filename))

    if explanation_file:
        if explanation_file.content_length > app.config['MAX_CONTENT_PATH']:
            flash('Explanation file size exceeds the limit of 1 MB.')
            return redirect(url_for('administrator2'))
        explanation_filename = secure_filename(explanation_file.filename)
        explanation_file.save(os.path.join(app.config['UPLOAD_FOLDER'], explanation_filename))

    add_question_sql = f"""
    INSERT INTO {table_name} (question, explanation) VALUES (:question, :explanation)
    """
    db.session.execute(db.text(add_question_sql), {
        'question': question_text if question_text else f"{app.config['UPLOAD_FOLDER']}/{question_filename}",
        'explanation': explanation_text if explanation_text else f"{app.config['UPLOAD_FOLDER']}/{explanation_filename}"
    })
    db.session.commit()
    return redirect(url_for('administrator2'))

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check your email and password', 'danger')
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    # Clear the session
    session.clear()
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['firstName']
        second_name = request.form['secondName']
        phone_no = request.form['phoneNo']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(first_name=first_name, second_name=second_name, phone_no=phone_no, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/add_to_favorites/<string:table_name>/<int:question_id>', methods=['POST'])
def add_to_favorites(table_name, question_id):
    if 'user_id' not in session:
        flash('You must be logged in to add to favorites.', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Fetch the question and explanation from the specified table
    query = f"SELECT question, explanation FROM {table_name} WHERE id = :flashcard_id"
    flashcard = db.session.execute(db.text(query), {'flashcard_id': question_id}).fetchone()
    
    if not flashcard:
        flash('Flashcard not found.', 'danger')
        return redirect(url_for('view_flashcards', table_name=table_name))
    
    question, explanation = flashcard  # Unpacking the tuple

    # Check if the flashcard is already in favorites
    existing_favorite = Favorite.query.filter_by(user_id=user_id, flashcard_id=question_id, table_name=table_name).first()
    if existing_favorite:
        flash('Flashcard is already in favorites.', 'info')
        return redirect(url_for('view_flashcards', table_name=table_name))

    new_favorite = Favorite(user_id=user_id, flashcard_id=question_id, table_name=table_name, question=question, explanation=explanation)
    db.session.add(new_favorite)
    db.session.commit()

    flash('Flashcard added to favorites.', 'success')
    return redirect(url_for('view_flashcards', table_name=table_name))


def alter_favorite_table():
    with db.engine.connect() as conn:
        result = conn.execute(db.text("PRAGMA table_info(favorite);")).fetchall()
        columns = [column[1] for column in result]
        
        if 'question' not in columns:
            conn.execute(db.text("ALTER TABLE favorite ADD COLUMN question TEXT;"))
        
        if 'explanation' not in columns:
            conn.execute(db.text("ALTER TABLE favorite ADD COLUMN explanation TEXT;"))

@app.route('/view_favorites')
def view_favorites():
    if 'user_id' not in session:
        flash('You must be logged in to view favorites.', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']
    favorites = Favorite.query.filter_by(user_id=user_id).all()

    return render_template('view_favorites.html', favorite_flashcards=favorites)

@app.route('/remove_from_favorites/<string:table_name>/<int:flashcard_id>', methods=['POST'])
def remove_from_favorites(table_name, flashcard_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify(success=False, message='You must be logged in to perform this action.')

    favorite = Favorite.query.filter_by(user_id=user_id, table_name=table_name, flashcard_id=flashcard_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify(success=True)
    return jsonify(success=False, message='Favorite not found.')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        try:
            alter_favorite_table()
        except Exception as e:
            print(f"Error altering table: {e}")
    app.run(debug=True)
