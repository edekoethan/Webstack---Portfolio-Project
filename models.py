from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(150), nullable=False)
    question = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=False)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    flashcard_id = db.Column(db.Integer, nullable=False)
