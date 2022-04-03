import re
from flask import Flask
from flask import request, render_template, session
from flask import redirect, url_for
from flask_session import Session
from flask_mail import Mail,Message
import hashlib
import os
from string_utility import *
import cryptocode

#Store the data on memory(volatile)
data_dict={}
#init the flask app instance
app = Flask(__name__)
#session configuration
app.config['SESSION PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'
Session(app) #add cookies/session functionality for temp Storage

#SMTP Configuration
app.config['MAIL_SERVER']='smtp.gmail.com
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'bilal.it@gmail.com'
app.config['MAIL_PASSWORD'] = 'acauuyeufonnxwmy'
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

#end points for account management
@app.route("/",methods=['GET','POST'])
def index():
  return redirect(url_for('login'))

@app.route("/login/", methods=['GET', 'POST'])
def login():
  if request.method=='GET':
    return render_template('login.html')
  elif request.method=='POST':
    email = request.form.get('email')
    if email in data_dict.keys():
      password =request.form.get('password')
      #create hash from the password
      salt = data_dict[email]['salt']
      password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
      if password_hash == data_dict[email]['password_hash']:
        return redirect(url_for('send'))
      else:
        return render_template('login.html',error='Your Username and Password do not match')
      return render_template('login.html',error='email does not exist, please signup to create the account')
