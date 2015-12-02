from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///catalog.db'
db = SQLAlchemy(app)


class Manufacturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    models = db.relationship('Model',
                             backref='manufacturer',
                             uselist=False,
                             order_by="Model.name")

    def __init__(self, name):
        self.name = name


class Model(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    picUrl = db.Column(db.Text)
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('manufacturer.id'))

    def __init__(self, name, description, picUrl):
        self.name = name
        self.description = description
        self.picUrl = picUrl


if __name__ == "__main__":
    db.create_all()
