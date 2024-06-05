from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Replace with your actual database credentials
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:00781227.mYSQL@localhost/pharmacology'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Alzheimer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    explanation = db.Column(db.String(255), nullable=False)

@app.route('/')
def index():
    questions = Alzheimer.query.all()
    return render_template('index.html', questions=questions)

@app.route('/add', methods=['POST'])
def add_question():
    question = request.form['question']
    explanation = request.form['explanation']
    new_entry = Alzheimer(question=question, explanation=explanation)
    db.session.add(new_entry)
    db.session.commit()
    return 'Question added successfully'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)

