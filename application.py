from bleach import clean
from catalog.database.db import Manufacturer, Model, db
from dicttoxml import dicttoxml
from flask import Flask, render_template, request, redirect, url_for, flash,\
    jsonify, Response, session
from flask_bootstrap import Bootstrap
from flask_wtf import Form, CsrfProtect
from oauth2client import client
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired

# #############################################################################
# App setup
# #############################################################################

app = Flask(__name__)

app.config['SECRET_KEY'] = 'XAZm&yg2hP#DEDnXStS2Qwt00Gy%PdG%kh*EmMbijyX4oBY^ZY'
app.config['WTF_CSRF_ENABLED'] = True

CsrfProtect(app)
Bootstrap(app)

# #############################################################################
# Read functions
# #############################################################################


@app.route("/")
def manufacturerList():
    logged_in = True if 'credentials' in session else False
    manufacturers = Manufacturer.query.order_by(Manufacturer.name).all()
    return render_template("manufacturerlist.html",
                           manufacturers=manufacturers,
                           logged_in=logged_in)


@app.route("/<int:manufacturer_id>/")
def manufacturerPage(manufacturer_id):
    logged_in = True if 'credentials' in session else False
    manufacturer = Manufacturer.query.filter_by(id=manufacturer_id).one()
    models = manufacturer.models.all()
    return render_template("manufacturerpage.html",
                           manufacturer=manufacturer,
                           models=models,
                           logged_in=logged_in)


@app.route("/<int:manufacturer_id>/<int:model_id>/")
def modelPage(manufacturer_id, model_id):
    logged_in = True if 'credentials' in session else False
    manufacturer = Manufacturer.query.filter_by(id=manufacturer_id).one()
    model = manufacturer.models.filter_by(id=model_id).one()
    return render_template("modelpage.html",
                           manufacturer=manufacturer,
                           model=model,
                           logged_in=logged_in)

# #############################################################################
# Login functions
# #############################################################################


@app.route("/login/")
def login():
    print('credentials' in session)
    if 'credentials' not in session:
        return redirect(url_for('loginCallback'))
    else:
        return redirect(url_for('newManufacturerPage'))


# Taken from the Google OAuth documentation.
@app.route("/login/callback/")
def loginCallback():
    flow = client.flow_from_clientsecrets(
        'client_secrets.json',
        scope='https://www.googleapis.com/auth/userinfo.email',
        redirect_uri='http://localhost:5000/login/callback/')
    if 'code' not in request.args:
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)
    else:
        auth_code = request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        session['credentials'] = credentials.to_json()
        return redirect(url_for('manufacturerList'))


@app.route("/logout/")
def logout():
    session.clear()
    return redirect(url_for('manufacturerList'))

# #############################################################################
# Create functions
# #############################################################################


@app.route("/new/", methods=['GET', 'POST'])
def newManufacturerPage():
    logged_in = True if 'credentials' in session else False
    if not logged_in:
        return redirect(url_for('manufacturerList'))
    form = ManufacturerEditForm()
    # Handle as a get when first going to the page.
    if request.method == 'GET':
        return render_template("newmanufacturerpage.html", form=form)
    # When the form comes back, it's a post.
    elif request.method == 'POST':
        if form.validate_on_submit():
            manufacturer = Manufacturer(clean(request.form['name']))
            db.session.add(manufacturer)
            db.session.commit()
            # Re-bind manufacturer after commit or else it lacks an id.
            manufacturer = Manufacturer.query.filter_by(
                name=manufacturer.name).one()
            return redirect(url_for('manufacturerPage',
                                    manufacturer_id=manufacturer.id))
        else:
            # If there were more validations, we would have to handle them more
            # intelligently here rather than assuming this is the only
            # possible error.
            flash("This field may not be blank.")
            return redirect(url_for('newManufacturerPage'))
    else:
        raise RuntimeError  # In case of breaking to methods= argument


@app.route("/<int:manufacturer_id>/new/", methods=['GET', 'POST'])
def newModelPage(manufacturer_id):
    logged_in = True if 'credentials' in session else False
    manufacturer = Manufacturer.query.filter_by(id=manufacturer_id).one()
    if not logged_in:
        redirect(url_for('manufacturerPage', manufacturer_id=manufacturer.id))
    choices = [(m.id, m.name) for m in Manufacturer.query.all()]
    form = ModelEditForm(mfg=manufacturer.id)
    form.mfg.choices = choices
    if request.method == 'GET':
        return render_template("newmodelpage.html",
                               manufacturer=manufacturer,
                               form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            model = Model(
                clean(request.form['name']), clean(request.form[
                    'description']), clean(request.form['picUrl']))
            manufacturer = Manufacturer.query.filter_by(
                id=request.form['mfg']).one()
            manufacturer.models.append(model)
            db.session.commit()
            model = Model.query.filter_by(name=model.name).first()
            return redirect(url_for('modelPage',
                                    manufacturer_id=manufacturer.id,
                                    model_id=model.id))
        else:
            print(form.errors)
            flash("The Model Name may not be blank.")
            return redirect(url_for('newModelPage',
                                    manufacturer_id=manufacturer.id))
    else:
        raise RuntimeError

# #############################################################################
# Update functions
# #############################################################################

# These are similar to the create functions, so refactoring might be in order
# to abstract out the similarities.


@app.route("/<int:manufacturer_id>/edit/", methods=['GET', 'POST'])
def editManufacturerPage(manufacturer_id):
    logged_in = True if 'credentials' in session else False
    manufacturer = Manufacturer.query.filter_by(id=manufacturer_id).one()
    if not logged_in:
        # This approach simply redirects the user if they manually type the URL for
        # the edit page.
        return redirect(url_for('manufacturerPage',
                                manufacturer_id=manufacturer.id))
    form = ManufacturerEditForm(name=manufacturer.name)
    if request.method == 'GET':
        # Set default values.
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
    logged_in = True if 'credentials' in session else False
    manufacturer = Manufacturer.query.filter_by(id=manufacturer_id).one()
    model = manufacturer.models.filter_by(id=model_id).one()
    if not logged_in:
        return redirect(url_for('modelPage',
                                manufacturer_id=manufacturer.id,
                                model_id=model.id))
    choices = [(m.id, m.name) for m in Manufacturer.query.all()]
    form = ModelEditForm(mfg=manufacturer.id,
                         name=model.name,
                         picUrl=model.picUrl,
                         description=model.description)
    # Choices only renders once, per the documentation, so to set the default
    # dynamically, we have to set the default when instatiating the form, then
    # assign the choices list after instantiation or it won't render.
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
    logged_in = True if 'credentials' in session else False
    manufacturer = Manufacturer.query.filter_by(id=manufacturer_id).one()
    if not logged_in:
        return redirect(url_for('manufacturerPage',
                                manufacturer_id=manufacturer.id))
    models = manufacturer.models.filter_by(
        manufacturer_id=manufacturer.id)  # How do we order_by here?
    return render_template('confirmmanufacturerdelete.html',
                           manufacturer=manufacturer,
                           models=models)


@app.route("/<int:manufacturer_id>/<int:model_id>/delete/")
def deleteModelPage(manufacturer_id, model_id):
    logged_in = True if 'credentials' in session else False
    manufacturer = Manufacturer.query.filter_by(id=manufacturer_id).one()
    model = Model.query.filter_by(id=model_id).one()
    if not logged_in:
        return redirect(url_for('modelPage',
                                manufacturer_id=manufacturer.id,
                                model_id=model.id))
    return render_template('confirmmodeldelete.html',
                           manufacturer=manufacturer,
                           model=model)


@app.route("/<int:manufacturer_id>/delete/execute/")
def executeDeleteManufacturer(manufacturer_id):
    logged_in = True if 'credentials' in session else False
    if (logged_in):
        manufacturer = Manufacturer.query.filter_by(id=manufacturer_id).one()
        db.session.delete(manufacturer)
        db.session.commit()
    return redirect(url_for('manufacturerList'))


@app.route("/<int:manufacturer_id>/<int:model_id>/delete/execute/")
def executeDeleteModel(manufacturer_id, model_id):
    logged_in = True if 'credentials' in session else False
    if logged_in:
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
    mfg = SelectField(coerce=int)

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
    # app.debug = True  # Remove in production.
    app.run()
