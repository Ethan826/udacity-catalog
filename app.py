from flask import Flask, render_template, request, redirect, url_for, flash
from database.db import Manufacturer, db
from flask_wtf import Form, CsrfProtect
from wtforms import StringField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = 'qRdXDN##DjcWUfvE@@J#e^nlu%LpoB!qS9Y9Z17IAwgu&cn2A4'
CsrfProtect(app)


@app.route("/")
def manufacturerlist():
    manufacturers = Manufacturer.query.all()
    return render_template("manufacturerlist.html",
                           manufacturers=manufacturers)


@app.route("/<int:manufacturer_id>/")
def manufacturerPage(manufacturer_id):
    manufacturer = Manufacturer.query.filter_by(id=manufacturer_id).one()
    models = manufacturer.models.query.filter_by(
        manufacturer_id=manufacturer.id)
    return render_template("manufacturerpage.html",
                           manufacturer=manufacturer,
                           models=models)


@app.route("/<int:manufacturer_id>/<int:model_id>/")
def modelPage(manufacturer_id, model_id):
    manufacturer = Manufacturer.query.filter_by(id=manufacturer_id).one()
    model = manufacturer.models.query.filter_by(id=model_id).one()
    return render_template("modelpage.html",
                           manufacturer=manufacturer,
                           model=model)


@app.route("/<int:manufacturer_id>/edit/", methods=['GET', 'POST'])
def editManufacturerPage(manufacturer_id):
    manufacturer = Manufacturer.query.filter_by(id=manufacturer_id).one()
    form = EditForm()
    if request.method == 'GET':
        return render_template("editmanufacturerpage.html",
                               manufacturer=manufacturer,
                               form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            manufacturer.name = request.form['name']
            db.session.commit()
            return redirect(url_for('manufacturerPage',
                                    manufacturer_id=manufacturer.id))
        else:
            flash("This field may not be blank.")
            return redirect(url_for('editManufacturerPage',
                                    manufacturer_id=manufacturer.id))
    else:
        raise RuntimeError


@app.route("/<int:manufacturer_id>/<int:model_id>/edit/",
           methods=['GET', 'POST'])
def editModelPage(manufacturer_id, model_id):
    manufacturer = Manufacturer.query.filter_by(id=manufacturer_id).one()
    model = manufacturer.models.query.filter_by(id=model_id).one()
    form = EditForm()
    if request.method == 'GET':
        return render_template("editmodelpage.html",
                               manufacturer=manufacturer,
                               model=model,
                               form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            model.name = request.form['name']
            db.session.commit()
            return redirect(url_for('modelPage',
                                    manufacturer_id=manufacturer.id,
                                    model_id=model.id))
        else:
            flash("This field may not be blank.")
            return redirect(url_for('editModelPage',
                                    manufacturer_id=manufacturer.id,
                                    model_id=model.id))
    else:
        raise RuntimeError


class EditForm(Form):
    name = StringField('name', validators=[DataRequired()])


if __name__ == "__main__":
    app.debug = True
    app.run()
