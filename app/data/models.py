from app import db
from datetime import datetime

class DataFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256))
    filepath = db.Column(db.String(512))
    uploaded_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    analyses = db.relationship('Analysis', backref='data_file', lazy='dynamic')
    predictions = db.relationship('Prediction', backref='data_file', lazy='dynamic')

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_file_id = db.Column(db.Integer, db.ForeignKey('data_file.id'))
    analysis_type = db.Column(db.String(128))
    parameters = db.Column(db.Text)
    result_path = db.Column(db.String(512))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_file_id = db.Column(db.Integer, db.ForeignKey('data_file.id'))
    model_type = db.Column(db.String(128))
    target_column = db.Column(db.String(128))
    parameters = db.Column(db.Text)
    metrics = db.Column(db.Text)
    result_path = db.Column(db.String(512))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)