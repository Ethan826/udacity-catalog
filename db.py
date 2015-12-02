from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///catalog.db'
db = SQLAlchemy(app)


class Manufacturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)

    def __init__(self, name):
        self.name = name


class Model(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    picUrl = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('manufacturer.id'))
    category = db.relationship('Manufacturer', backref=db.backref('models'))

    def __init__(self, name, description, picUrl, category_id):
        self.name = name
        self.description = description
        self.picUrl = picUrl
        self.category_id = category_id


if __name__ == "__main__":
    db.create_all()
