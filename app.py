from flask import Flask, request, make_response, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_httpauth import HTTPBasicAuth


class Config():
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")

app = Flask(__name__)
app.config.from_object(Config)
db= SQLAlchemy(app)
migrate=Migrate(app,db)
basic_auth = HTTPBasicAuth()

@basic_auth.verify_password
def verify_password(email, password):
    u = User.query.filter_by(email=email).first()
    if u is None:
        return False
    g.current_user = u
    return u.check_hashed_password(password)


class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, index=True)
    password = db.Column(db.String)
    recipes = db.relationship("Recipe", backref='author',lazy="dynamic", cascade ='all, delete-orphan')

    def hash_password(self, original_password):
        return generate_password_hash(original_password)

    def check_hashed_password(self, login_password):
        return check_password_hash(self.password, login_password)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def from_dict(self,data):
        self.email = data['email']
        self.password=self.hash_password(data['password'])

    def to_dict(self):
        return {"user_id": self.user_id, "email":self.email}



class Recipe(db.Model):
    __tablename__ = 'recipe'

    recipe_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    body = db.Column(db.String)
    user_id = db.Column(db.ForeignKey('user.user_id'))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def from_dict(self, data):
        self.title = data['title']
        self.body = data['body']
        self.user_id = data['user_id']

    def to_dict(self):
        return {"recipe_id": self.recipe_id, "title":self.title, "body":self.body, "user_id":self.user_id}

@app.get('/user')
def get_all_users():
    users = User.query.all()
    #creates a list of user dictionaries for ever user in user
    users = [user.to_dict() for user in users]
    return make_response({"Users": users})

@app.get('/user/<int:id>')
def get_specific_user(id):
    user = User.query.get(id)
    return make_response({"User": user.to_dict()})

@app.post('/user')
def create_user():
    data = request.get_json()
    new_user = User()
    new_user.from_dict(data)
    new_user.save()
    return make_response("success user created", 200)

@app.put('/user/<int:id>')
def edit_user(id):
    data = request.get_json()
    user = User.query.get(id)
    if 'email' in data:
        user.email = data['email']
    if 'password' in data:
        user.password = data['password']
    user.save()
    return make_response("success user updated", 200)

@app.delete('/user/<int:id>')
def delete_user(id):
    user = User.query.get(id)
    user.delete()
    return make_response("success user deleted", 200)

@app.get('/recipe')
def get_all_recipes():
    recipes = Recipe.query.all()
    recipes = [recipe.to_dict for recipe in recipes]
    return make_response({"Recipes": recipes})

@app.get('/recipe/<int:id>')
def get_specific_recipe(id):
    recipe = Recipe.query.get(id)
    return make_response({"Recipe": recipe})

@app.post('/recipe')
def create_recipe():
    data = request.get_json()
    new_recipe = Recipe()
    new_recipe.from_dict(data)
    new_recipe.save()
    return make_response("success recipe created", 200)

@app.put('/recipe/<int:id>')
def edit_recipe(id):
    data = request.get_json()
    recipe = Recipe.query.get(id)
    if 'title' in data:
        recipe.title = data['title']
    if 'body' in data:
        recipe.title = data['body']
    recipe.save()
    return make_response("success recipe updated", 200)

@app.delete('/recipe/<int:id>')
def delete_recipe(id):
    recipe = Recipe.query.get(id)
    recipe.delete()
    return make_response("success recipe deleted", 200)

@app.get('/user/recipes/<int:id>')
def user_recipes(id):
    recipes = Recipe.query.filter_by(user_id=id)
    recipes = [recipe.to_dict() for recipe in recipes]
    return make_response({"My Recipes": recipes})






