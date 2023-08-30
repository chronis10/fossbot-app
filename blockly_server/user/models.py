from flask import Flask, jsonify, request, session, redirect, flash
# import uuid

class User:

    def start_session(self, user):
        session['logged_in'] = True
        session['user'] = user
        return jsonify(user), 200

    # def signup(self):
    #     print(request.form)
        
    #     # Create the user object
    #     user = {
    #         "_id": uuid.uuid4().hex,
    #         "name": request.form.get('name')
    #     }

    def signout(self):
        session.clear()
        return redirect('/')

    def login(self):
        user = request.args.get('name')
        return self.start_session(user)