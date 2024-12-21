# models.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Letter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(100), nullable=True)
    date_sent = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)  # 좋아요 수를 위한 필드 추가

    def __repr__(self):
        return f'<Letter {self.sender_name}>'
