from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from db import Manufacturer, Model

app = Flask(__name__)


@app.route("/")
@app.route("/manufacturers/")
def manufacturerlist():
    manufacturers = Manufacturer.query.all()
    return render_template("manufacturerlist.html",
                           manufacturers=manufacturers)


@app.route("/manufacturers/<int:manufacturer_id>/")
def manufacturerPage(manufacturer_id):
    manufacturer = Manufacturer.query.filter_by(id=manufacturer_id).one()
    # Problem defining models
    return render_template("manufacturerpage.html",
                           manufacturer=manufacturer,
                           models=models)


@app.route("/manufacturers/<int:manufacturer_id>/<int:model_id>/")
def modelPage(manufacturer_id, model_id):
    manufacturer = Manufacturer.query.filter_by(id=manufacturer_id).one()
    model = manufacturer.models # This is the problem
    return render_template("modelpage.html",
                           manufacturer=manufacturer,
                           model=model)


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0")
