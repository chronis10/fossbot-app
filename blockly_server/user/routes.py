from flask import Flask
from app import app
from user.models import User

@app.route('/user/signout')
def signout():
    return User().signout()

@app.route('/user/login', methods=['POST'])
def login():
    return User().login()