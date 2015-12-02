from flask import Flask, render_template
from db import Manufacturer

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
    models = manufacturer.models.query.filter_by(manufacturer_id=manufacturer.id)
    return render_template("manufacturerpage.html",
                           manufacturer=manufacturer,
                           models=models)


@app.route("/manufacturers/<int:manufacturer_id>/<int:model_id>/")
def modelPage(manufacturer_id, model_id):
    manufacturer = Manufacturer.query.filter_by(id=manufacturer_id).one()
    model = manufacturer.models.query.filter_by(id=model_id).one()
    return render_template("modelpage.html",
                           manufacturer=manufacturer,
                           model=model)


if __name__ == "__main__":
    app.debug = True
    app.run()
