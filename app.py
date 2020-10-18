from flask import Flask, render_template, request, jsonify, redirect, flash
import cv2
import csv
import numpy as np
from PIL import Image, ImageDraw
import functools, operator
from tensorflow.keras.models import load_model
from werkzeug.utils  import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager , UserMixin , login_required ,login_user, logout_user,current_user

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db.db'
app.config['SECRET_KEY']='90123'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    username = db.Column(db.String(200))
    email = db.Column(db.String(200))
    password = db.Column(db.String(300))


@login_manager.user_loader
def get(id):
    return User.query.get(id)

@app.login_manager.unauthorized_handler
def unauth_handler():
    return jsonify(success=False,
                   data={'login_required': True},
                   message='Unauthorized, You need to login first to access this page'), 401

@app.errorhandler(404)
def not_found(error):
  resp = jsonify( { 
    u'status': 404, 
    u'message': u'Resource not found' 
    })
  resp.status_code = 404
  return resp
  
#We can also implement checks and error handling for login and reset.
# ***NOT IMPLEMENTING IT RIGHT NOW*** #
@app.route('/home',methods=['GET'])
@login_required
def get_home():
    return render_template('index.html',username=current_user.username)

@app.route('/',methods=['GET'])
def get_login():
    return render_template('login.html')

@app.route('/signup',methods=['GET'])
def get_signup():
    return render_template('signup.html')

@app.route('/reset', methods=['GET'])
def reset():
    # ***NOT IMPLEMENTING IT RIGHT NOW*** #
    return render_template('reset.html')

@app.route('/',methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username,password=password).first()
    if not user:
        flash('Please check your login credentials.')
        return redirect('/')
    login_user(user)
    return redirect('/home')

@app.route('/signup',methods=['POST'])
def signup_post():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()   
    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect('/signup')
    new_user = User(email=email, username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    flash('You have signed up successfully')
    return redirect('/signup')

@app.route('/logout',methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect('/')


if __name__=='__main__':
    app.run(debug=True)

