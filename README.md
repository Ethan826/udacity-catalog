# Civil Airplane Catalog App

Python 3 is required.

From the shell, run the following commands to start up this application:

    $ git clone https://github.com/Ethan826/udacity-catalog.git
    $ cd udacity-catalog/

Edit the `catalog.py` file to update the secret key to permit Google OAuth login.
    
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip3 install -r requirements.txt
    $ cd database
    $ python3 db.py
    $ python3 populate_db.py
    $ cd ..
    $ python3 application.py

Now launch your browser and navigate to `http://localhost:5000/`.

You can now browse the catalog. To make changes, you must sign in through
your Google account.

There are two API endpoints: one for JSON at `http://localhost:5000/json/`
and one for XML at `http://localhost:5000/xml/`.

To exit the Python 3 virtualenv, issue

    $ deactivate
