from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Alzheimer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(256), nullable=False)
    explanation = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return f'<Alzheimer {self.question}>'
