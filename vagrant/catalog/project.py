from flask import Flask, render_template, url_for, request, redirect, flash, jsonify

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem, User

# Imports for use of google login
from flask import session as login_session
import random, string

# Imports for oauth client
from oauth2client.client import flow_from_clientsecrets #stores client id, client secret, and other oauth2 parameters
from oauth2client.client import FlowExchangeError #Catch errors when trying to exchange access tokens
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

# Start application
app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenuwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/recipe-catalog')
def mainPage():
    pass

#CATEGORY SECTION
@app.route('/recipe-catalog/<int:category_id')
def viewCategory():
    pass
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Recipe).filter_by(category_id=category_id).all()

@app.route('/recipe-catalog/new/', methods=["GET", "POST"])
def createCategory():
    pass
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == "POST":
        pass
    else:
        return render_template("newCategory.html")

@app.route('/recipe-catalog/<int:category_id>', methods=["GET", "POST"])
def editCategory():
    pass
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == "POST":
        pass
        category = session.query(Category).filter_by(id=category_id).one()
        #TODO: Add features for editing
    else:
        #TODO: Create editCategory.html
        return render_template("editCategory.html")

@app.route('/recipe-catalog/<int:category_id>', methods=["GET", "POST"])
def deleteCategory():
    pass
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == "POST":
        pass
        category = session.query(Category).filter_by(id=category_id).one()
        session.delete(category)
        session.commit()

        flash("%(old)s was deleted from the site."%{"old":old_name})
        return redirect(url_for('viewCategory'))
    else:
        return render_template("deleteCategory.html")

#RECIPE SECTION
@app.route('/recipe-catalog/<int:category_id>/<int:recipe_id>')
def viewRecipe():
    pass
    return render_template("recipe")

@app.route('/recipe-catalog/<int:category_id>/new', methods=["GET", "POST"])
def createRecipe():
    pass
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == "POST":
        pass
        #TODO
        newRecipe = Recipe(
            name = request.form['name'],
            restaurant_id = restaurant_id,
            user_id=login_session['user_id']
            )
        session.add(newItem)
        session.commit()

        flash("New recipe created!")
        return redirect(url_for('viewRecipe', category_id=category_id, recipe_id=recipe_id))
    else:
        return render_template("newCategory.html")

@app.route('/recipe-catalog/<int:category_id>/<int:recipe_id>', methods=["GET", "POST"])
def editRecipe():
    pass
    #TODO: MODIFY BELOW CODE TO REFLECT PAGE FOR EDITING RECIPES
    if 'username' not in login_session:
        return redirect('/login')
    item = session.query(Recipe).filter_by(id=recipe_id).one()
    if request.method == "POST":
        old_name = item.name
        item.name = request.form['name']
        session.add(item)
        session.commit()
        flash("%(old)s changed to %(name)s" %{'old':old_name,'name':item.name})
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editMenuItem.html', item=item)
    return "page to edit a menu item. Task 2 complete!"

@app.route('/recipe-catalog/<int:category_id>/<int:recipe_id>', methods=["GET", "POST"])
def deleteRecipe():
    pass
    #TODO: MODIFY BELOW CODE TO REFLECT PAGE FOR DELETING RECIPES
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == "POST":
        pass
        recipe = session.query(Recipe).filter_by(id=recipe_id).one()
        session.delete(item)
        session.commit()

        flash("%(old)s was deleted from the site."%{"old":old_name})
        return redirect(url_for('restaurantMenu', category_id=category_id))
    else:
        return render_template("deleteCategory.html")

#RUN APPLICATION
if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='0.0.0.0', port=5000)