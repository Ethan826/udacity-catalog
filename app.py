from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from db import Category, Item

app = Flask(__name__)


@app.route("/")
def hello():
    return render_template("main.html")


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0")
