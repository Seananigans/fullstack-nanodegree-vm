from flask import Flask, render_template, url_for, request, redirect, flash, jsonify

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound
from database_setup import Base, Recipe, Category, User

# Imports for use of google login
from flask import session as login_session
import random, string

# Imports for oauth client
from oauth2client.client import flow_from_clientsecrets #stores client id, client secret, and other oauth2 parameters
from oauth2client.client import FlowExchangeError #Catch errors when trying to exchange access tokens
import httplib2
import json
from time import sleep
from flask import make_response
import requests
from app_secret import app_secret as apscret

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

# Start application
app = Flask(__name__)

engine = create_engine('sqlite:///recipesite.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except MultipleResultsFound, e:
        print e
        user = session.query(User).filter_by(email=email).first()
        return user.id
    except:
        return None

def getUserInfo(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return user

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'],
        picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).one()
    return user.id

# Create a state token to prevent request forgery.
# Store it in the session for later validation
@app.route('/login')
def showLogin():
    state = "".join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template("login.html", STATE=state)

# FACEBOOK LOGIN API
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s" % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]


    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    print "url sent for API access:%s"% url
    print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists

    user_id = getUserID(email=login_session['email'])

    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    flash("Now logged in as %s" % login_session['username'])
    return render_template("loginSuccess.html", login_session=login_session)

@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session.get('facebook_id')
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return redirect(url_for('showLogin'))

@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope="")
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    #Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 501)
        response.headers['Content-Type'] = 'application/json'
    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match given user ID"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."),
            401)
        response.headers['Content-Type'] = 'application/json'
        return response
    #Check to see if user is alread logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'),
            200)
        response.headers['Content-Type'] = 'application/json'

    #Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    #Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt':'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    login_session['username'] = data['name']
    login_session['provider'] = 'google'
    login_session['picture'] = data['picture']
    login_session['email'] = data['email'].replace("\u0040", "@")

    user_id = getUserID(login_session['email'])
    if user_id == None:
        createUser(login_session)
    login_session['user_id'] = user_id

    flash("You are now logged in as %s" %login_session['username'])
    return render_template("loginSuccess.html", login_session=login_session)

#DISCONNECT - Revoke a current user's token and reset their login_session
@app.route("/gdisconnect")
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = "https://accounts.google.com/o/oauth2/revoke?token=%s" %access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        #Reset the user's session.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['user_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['provider']

        response = make_response(
            json.dumps("Successfully disconnected."), 200)
        response.headers['Content-Type'] = "application/json"
        return redirect(url_for('showLogin'))
    else:
        print "*"*400
        print result['status']
        print "$"*400
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps("Failed to revoke token for given user."), 400)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('showLogin'))

#Making an API Endpoint (GET Request)
@app.route('/recipe-catalog/JSON/')
def recipe_catalogJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[i.serialize for i in categories])

@app.route('/recipe-catalog/category/<int:category_id>/JSON/')
def recipe_categoryJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    return jsonify(category=category.serialize)

@app.route('/recipe-catalog/recipe/<int:recipe_id>/JSON/')
def recipe_recipeJSON(recipe_id):
    recipe = session.query(Recipe).filter_by(id=recipe_id).one()
    return jsonify(recipe=recipe.serialize)

@app.route('/')
@app.route('/recipe-catalog/')
def mainPage():
    categories = session.query(Category).all()
    if 'username' in login_session:
        return render_template("mainpage.html",
            categories = categories,
            login_session = login_session)
    else:
        return render_template("mainpage.html",
            categories= categories)

#CATEGORY SECTION
@app.route('/recipe-catalog/category/<int:category_id>/')
def viewCategory(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    recipes = session.query(Recipe).filter_by(category_id=category_id).all()
    return render_template("viewCategory.html",
        category = category,
        recipes = recipes,
        login_session = login_session)

@app.route('/recipe-catalog/category/new/', methods=["GET", "POST"])
def createCategory():
    # Check to see if there is a user logged in
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == "POST":
        # Retrieve new information
        name = request.form["name"]
        description = request.form["description"]
        if len(name)<1:
            error = "Please fill in the name area."
            return render_template("newCategory.html",
                name=name,
                description=description,
                error=error,
                login_session = login_session)
        user_id = login_session['user_id']
        # Set new values
        newCategory = Category(
            name = name,
            description = description,
            user_id = user_id)
        # Commit changes to database
        session.add(newCategory)
        session.commit()
        sleep(0.1)
        # Redirect
        flash("new category item created!")
        return redirect(url_for('viewCategory', category_id=newCategory.id))
    else:
        return render_template("newCategory.html",
            login_session = login_session)

@app.route('/recipe-catalog/category/<int:category_id>/edit/', methods=["GET", "POST"])
def editCategory(category_id):
    # Check to see if there is a user logged in
    if 'username' not in login_session:
        return redirect('/login')
    e_category = session.query(Category).filter_by(id=category_id).one()
    # Check to see that category creator and current user are the same
    if login_session['user_id'] != e_category.user_id:
        flash("You cannot edit a category that you did not create.")
        return redirect(url_for('viewCategory', category_id=e_category.id))
    if request.method == "POST":
        # Retrieve new information
        name = request.form["name"]
        description = request.form["description"]
        if len(name)<1:
            error = "Please fill in the name area."
            return render_template("newCategory.html",
                category=e_category,
                error=error,
                login_session = login_session)
        # Set new values
        e_category.name = name
        e_category.description = description
        # Commit changes to database
        session.add(e_category)
        session.commit()
        sleep(0.1)
        # Redirect
        flash("Category edited!")
        return redirect(url_for('viewCategory', category_id=e_category.id))
    else:
        return render_template("editCategory.html",
            category=e_category,
            login_session = login_session)

@app.route('/recipe-catalog/category/<int:category_id>/delete/', methods=["GET", "POST"])
def deleteCategory(category_id):
    # Check to see if there is a user logged in
    if 'username' not in login_session:
        return redirect('/login')
    d_category = session.query(Category).filter_by(id=category_id).one()
    # Check to see that category creator and current user are the same
    if login_session['user_id'] != d_category.user_id:
        flash("You cannot delete a category that you did not create.")
        return redirect(url_for('viewCategory', category_id=d_category.id))
    if request.method == "POST":
        old_name = d_category.name
        # Commit changes to database
        session.delete(d_category)
        session.commit()
        sleep(0.1)
        # Redirect
        flash("%(old)s was deleted from the site."%{"old":old_name})
        return redirect(url_for('mainPage'))
    else:
        return render_template("deleteCategory.html",
            category=d_category,
            login_session = login_session)

#RECIPE SECTION
@app.route('/recipe-catalog/recipe/<int:recipe_id>')
def viewRecipe(recipe_id):
    recipe = session.query(Recipe).filter_by(id=recipe_id).one()
    return render_template("viewRecipe.html",
        recipe=recipe,
        login_session = login_session)

@app.route('/recipe-catalog/category/<int:category_id>/recipe/new/', methods=["GET", "POST"])
def createRecipe(category_id):
    # Check to see if there is a user logged in
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == "POST":
        # Retrieve new information
        name = request.form['name']
        description = request.form['description']
        steps = request.form['steps']
        if not name or not steps or len(name)<1 or len(steps)<1:
            error = "Please make sure to fill in the name and the steps."
            return render_template("newRecipe.html",
                error=error,
                name=name,
                description=description,
                steps=steps)
        user_id = login_session['user_id']
        # Set new values
        newRecipe = Recipe(
            name = name,
            description = description,
            steps = steps,
            category_id = category_id,
            user_id = user_id)
        # Commit changes to database
        session.add(newRecipe)
        session.commit()
        sleep(0.1)

        flash("New recipe created!")
        return redirect(url_for('viewRecipe', recipe_id=newRecipe.id))
    else:
        category = session.query(Category).filter_by(id=category_id).one()
        return render_template("newRecipe.html",
            category= category,
            login_session= login_session)

@app.route('/recipe-catalog/recipe/<int:recipe_id>/edit/', methods=["GET", "POST"])
def editRecipe(recipe_id):
    if 'username' not in login_session:
        return redirect('/login')
    e_recipe = session.query(Recipe).filter_by(id=recipe_id).one()
    # Check to see that recipe creator and current user are the same
    if login_session['user_id'] != e_recipe.user_id:
        flash("You cannot edit a recipe that you did not create.")
        return redirect(url_for('viewRecipe', recipe_id=e_recipe.id))
    if request.method == "POST":
        old_name = e_recipe.name
        # Retrieve new information
        name = request.form['name']
        description = request.form['description']
        steps = request.form['steps']
        if not name or not steps or len(name)<1 or len(steps)<1:
            return render_template("newCategory.html",
                error=error,
                name=name,
                description=description,
                steps=steps,
                login_session = login_session)
        # Set new values
        e_recipe.name = name
        e_recipe.description = description
        e_recipe.steps = steps
        # Commit changes to database
        session.add(e_recipe)
        session.commit()
        sleep(0.1)
        # Redirect
        flash("%(old)s changed to %(name)s" %{'old':old_name, 'name':name})
        return redirect(url_for('viewRecipe', recipe_id=recipe_id))
    else:
        return render_template('editRecipe.html',
            recipe=e_recipe,
            login_session = login_session)

@app.route('/recipe-catalog/recipe/<int:recipe_id>/delete/', methods=["GET", "POST"])
def deleteRecipe(recipe_id):
    # Check to see if there is a user logged in
    if 'username' not in login_session:
        return redirect('/login')
    d_recipe = session.query(Recipe).filter_by(id=recipe_id).one()
    # Check to see that recipe creator and current user are the same
    if login_session['user_id'] != d_recipe.user_id:
        flash("You cannot delete a recipe that you did not create.")
        return redirect(url_for('viewRecipe', recipe_id=d_recipe.id))
    if request.method == "POST":
        old_name = d_recipe.name
        category_id = d_recipe.category_id
        # Commit changes to database
        session.delete(d_recipe)
        session.commit()
        sleep(0.1)
        # Redirect
        flash("%(old)s was deleted from the site."%{"old":old_name})
        return redirect(url_for('viewCategory', category_id=category_id))
    else:
        return render_template("deleteRecipe.html",
            recipe=d_recipe,
            login_session = login_session)

#RUN APPLICATION
if __name__ == '__main__':
    app.secret_key = apscret
    app.debug = True
    app.run(host='0.0.0.0', port=5000)