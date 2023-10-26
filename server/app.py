#!/usr/bin/env python3

from flask import request, session, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError


from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        json = request.get_json()

        if json.get('username'):
            new_user = User(username=json['username'])
            if json.get('image_url'):
                new_user.image_url = json['image_url']
            if json.get('bio'):
                new_user.bio = json['bio']
            # do password stuff here
            new_user.password_hash = json['password']

            db.session.add(new_user)
            db.session.commit()

            session['user_id'] = new_user.id

            response = make_response(new_user.to_dict(), 201)
            return response
        else:
            response = make_response({'error': 'Invalid credentials to create new user'}, 422)
            return response

class CheckSession(Resource):
    def get(self):
        if session.get('user_id'):
            user = User.query.filter(User.id==session['user_id']).first()
            response = make_response({
                "id": user.id,
                "username": user.username,
                "image_url": user.image_url,
                "bio": user.bio
            }, 200)
            return response
        else:
            response = make_response({'error': 'session not authroized'}, 401)
            return response

class Login(Resource):
    def post(self):

        json = request.get_json()

        username = json.get('username')
        password = json.get('password')

        user = User.query.filter(User.username == username).first()
        if user:
            if user.authenticate(password):
                session['user_id'] = user.id
                response = make_response({
                    "id": user.id,
                    "username": user.username,
                    "image_url": user.image_url,
                    "bio": user.bio
                }, 200)
                return response
        else:
            response = make_response({'error': 'unauthorized login'}, 401)
            return response


class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session['user_id'] = None
            return make_response({}, 204)
        else:
            return make_response({'error': 'user not logged in'}, 401)


class RecipeIndex(Resource):
    def get(self):
        if session.get('user_id'):
            user_recipes = Recipe.query.filter(Recipe.user_id == session.get('user_id')).all()
            arr_of_recipes = [{
                "title": recipe.title,
                "instructions": recipe.instructions,
                "minutes_to_complete": recipe.minutes_to_complete,
                "user": User.query.filter(User.id == session.get('user_id')).first().to_dict()
            } for recipe in user_recipes]
            response = make_response(arr_of_recipes, 200)
            return response
        else:
            return make_response({'error': 'user not logged in'}, 401)

    def post(self):
        json = request.get_json()
        if session.get('user_id'):
            new_recipe = Recipe(
                title=json['title'],
                instructions=json['instructions'],
                minutes_to_complete=json['minutes_to_complete'],
                user_id=session['user_id']
            )
            recipe_obj = {
                "title": new_recipe.title,
                "instructions": new_recipe.instructions,
                "minutes_to_complete": new_recipe.minutes_to_complete,
                "user": User.query.filter(User.id == session.get('user_id')).first().to_dict()
            }
            db.session.add(new_recipe)
            try:
                db.session.commit()
            except Exception as e:
                msg = str(e)
                return make_response({'error': msg}, 422)

            response = make_response(recipe_obj, 201)
            return response
        else:
            return make_response({'error': 'user not logged in'}, 401)

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)