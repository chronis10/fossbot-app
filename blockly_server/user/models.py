from flask import Flask, jsonify, request, session, redirect, flash
from app import user_db
import uuid

class User:

    def start_session(self, user):
        del user['password']
        session['logged_in'] = True
        session['user'] = user
        return jsonify(user), 200

    def signup(self):
        print(request.form)
        
        # Create the user object
        user = {
            "_id": uuid.uuid4().hex,
            "name": request.form.get('name')
        }

        # Check for existing username
        if user_db.users.find_one({"name": user['name']}):
            return jsonify({"error": "Username already in use"}), 400

        # Check for existing email address
        if user_db.users.find_one({"email": user['email']}):
            return jsonify({"error": "Email address already in use"}), 400

        # Insert new users into user collection
        if user_db.users.insert_one(user):
            return self.start_session(user)