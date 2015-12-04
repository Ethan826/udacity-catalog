from dicttoxml import dicttoxml
from bleach import clean
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_bootstrap import Bootstrap
from database.db import Manufacturer, Model, db
from flask_wtf import Form, CsrfProtect
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = 'qRdXDN##DjcWUfvE@@J#e^nlu%LpoB!qS9Y9Z17IAwgu&cn2A4'
CsrfProtect(app)
Bootstrap(app)


# #############################################################################
# Read functions
# #############################################################################

@app.route("/")
def manufacturerList():
    manufacturers = Manufacturer.query.order_by(Manufacturer.name).all()
    return render_template("manufacturerlist.html",
                           manufacturers=manufacturers)


@app.route("/<int:manufacturer_id>/")
def manufacturerPage(manufacturer_id):
    manufacturer = Manufacturer.query.filter_by(id=manufacturer_id).one()
    models = manufacturer.models.all()
    return render_template("manufacturerpage.html",
                           manufacturer=manufacturer,
                           models=models)


@app.route("/<int:manufacturer_id>/<int:model_id>/")
def modelPage(manufacturer_id, model_id):
    manufacturer = Manufacturer.query.filter_by(id=manufacturer_id).one()
    model = manufacturer.models.filter_by(id=model_id).one()
    return render_template("modelpage.html",
                           manufacturer=manufacturer,
                           model=model)


# #############################################################################
# Create functions
# #############################################################################

@app.route("/new/", methods=['GET', 'POST'])
def newManufacturerPage():
    form = ManufacturerEditForm()
    if request.method == 'GET':
        return render_template("newmanufacturerpage.html", form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            manufacturer = Manufacturer(clean(request.form['name']))
            db.session.add(manufacturer)
            db.session.commit()
            manufacturer = Manufacturer.query.filter_by(
                name=manufacturer.name).one()
            return redirect(url_for('manufacturerPage',
                                    manufacturer_id=manufacturer.id))
        else:
            flash("This field may not be blank.")
            return redirect(url_for('newManufacturerPage'))
    else:
        raise RuntimeError  # We probably can't get here because of the methods argument


@app.route("/<int:manufacturer_id>/new/", methods=['GET', 'POST'])
def newModelPage(manufacturer_id):
    manufacturer = Manufacturer.query.filter_by(id=manufacturer_id).one()
    choices = [(m.id, m.name) for m in Manufacturer.query.all()]
    form = ModelEditForm(mfg=manufacturer.id)
    form.mfg.choices = choices
    if request.method == 'GET':
        return render_template("newmodelpage.html",
                               manufacturer=manufacturer,
                               form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            model = Model(clean(request.form['name']), clean(request.form[
                          'description']), clean(request.form['picUrl']))
            manufacturer = Manufacturer.query.filter_by(
                id=request.form['mfg']).one()
            manufacturer.model.append(model)
            db.session.commit()
            model = Model.query.filter_by(model.name).one()
            return redirect(url_for('modelPage',
                                    manufacturer_id=manufacturer.id,
                                    model_id=model.id))
        else:
            flash("The Model Name may not be blank.")
            return redirect(url_for('newModelPage',
                                    manufacturer_id=manufacturer.id))
    else:
        raise RuntimeError


# #############################################################################
# Update functions
# #############################################################################

@app.route("/<int:manufacturer_id>/edit/", methods=['GET', 'POST'])
def editManufacturerPage(manufacturer_id):
    manufacturer = Manufacturer.query.filter_by(id=manufacturer_id).one()
    form = ManufacturerEditForm(name=manufacturer.name)
    if request.method == 'GET':
        return render_template("editmanufacturerpage.html",
                               manufacturer=manufacturer,
                               form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            manufacturer.name = clean(request.form['name'])
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
    model = manufacturer.models.filter_by(id=model_id).one()
    choices = [(m.id, m.name) for m in Manufacturer.query.all()]
    form = ModelEditForm(mfg=manufacturer.id, name=model.name,
                         picUrl=model.picUrl, description=model.description)
    form.mfg.choices = choices

    if request.method == 'GET':
        return render_template("editmodelpage.html",
                               manufacturer=manufacturer,
                               model=model,
                               form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            model.name = clean(request.form['name'])
            model.manufacturer = Manufacturer.query.filter_by(
                id=request.form['mfg']).one()
            model.picUrl = clean(request.form['picUrl'])
            model.description = clean(request.form['description'])
            db.session.commit()
            return redirect(url_for('modelPage',
                                    manufacturer_id=manufacturer.id,
                                    model_id=model.id))
        else:
            flash("The Model Name may not be blank.")
            return redirect(url_for('editModelPage',
                                    manufacturer_id=manufacturer.id,
                                    model_id=model.id))
    else:
        raise RuntimeError


# #############################################################################
# Delete functions
# #############################################################################

@app.route("/<int:manufacturer_id>/delete/")
def deleteManufacturerPage(manufacturer_id):
    manufacturer = Manufacturer.query.filter_by(id=manufacturer_id).one()
    models = manufacturer.models.filter_by(
        manufacturer_id=manufacturer.id)  # How do we order_by here?
    return render_template('confirmmanufacturerdelete.html',
                           manufacturer=manufacturer,
                           models=models)


@app.route("/<int:manufacturer_id>/<int:model_id>/delete/")
def deleteModelPage(manufacturer_id, model_id):
    manufacturer = Manufacturer.query.filter_by(id=manufacturer_id).one()
    model = Model.query.filter_by(id=model_id).one()
    return render_template('confirmmodeldelete.html',
                           manufacturer=manufacturer,
                           model=model)


@app.route("/<int:manufacturer_id>/delete/execute/")
def executeDeleteManufacturer(manufacturer_id):
    manufacturer = Manufacturer.query.filter_by(id=manufacturer_id).one()
    db.session.delete(manufacturer)
    db.session.commit()
    return redirect(url_for('manufacturerList'))


@app.route("/<int:manufacturer_id>/<int:model_id>/delete/execute/")
def executeDeleteModel(manufacturer_id, model_id):
    model = Model.query.filter_by(id=model_id).one()
    db.session.delete(model)
    db.session.commit()
    return redirect(url_for('manufacturerPage',
                            manufacturer_id=manufacturer_id,
                            model_id=model.id))


# #############################################################################
# Forms
# #############################################################################

class ManufacturerEditForm(Form):
    name = StringField('name', validators=[DataRequired()])


class ModelEditForm(Form):
    name = StringField('name', validators=[DataRequired()])
    picUrl = StringField('picUrl')
    description = TextAreaField('description')
    mfg = SelectField('Manufacturer')


# #############################################################################
# API functions
# #############################################################################

def createSiteDict():
    manufacturers = Manufacturer.query.all()
    data = {}
    for mfg in manufacturers:
        models = mfg.models
        mods = {}
        for mod in models:
            mods[mod.name] = {
                "picUrl": mod.picUrl,
                "description": mod.description
            }
        data[mfg.name] = mods
    return data


@app.route('/json/')
def emitJson():
    return jsonify(createSiteDict())


@app.route('/xml/')
def emitXml():
    return Response(dicttoxml(createSiteDict()), mimetype='text/xml')


# #############################################################################
# Main function
# #############################################################################

if __name__ == "__main__":
    app.debug = True
    app.run()
