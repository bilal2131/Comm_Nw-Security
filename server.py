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
app.config['MAIL_PORT'] = 564
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

@app.route("/signup/",methods=['GET','POST'])
def signup():
  if request.method=='GET':
    return render_template('sign_up.html')
elif request.method=='POST':
  global data_dict
  email_id = request.form.get('email').lower()
  password = request.form.get('password')
  if email_id in data_dict.keys():
    return render_template('sign_up.html',error='email already registered please use other email')
      
  #if email is not already registered
  salt = os.urandom(32)
  password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
      
  #send the activation message to activate account
  activation_string = random_string()
  title = 'activation of account'
  mail_obj = Message(title, sender = app.config['MAIL_USERNAME'], recipients = [email_id])
  mail_obj.body = f'code to activate your account is {activation_string}'
  mail.send(mail_obj)
      
  #store the data temporarily on session
  session['password_hash'] = password_hash
  session['salt'] = salt
  session['email'] = email_id
  session['activation_code'] = activation_string
  return redirect(url_for('activate'))

@app.route("/activate/",methods=['GET','POST'])
def activeate():
  if request.method=='GET':
    return render_template("activate.html")
  elif request.method=='POST':
    activation_code = request.form.get('code')
    if activation_code == session.get('activation_code'):
      #update the data_dict with empty elements
      email = session.get('email')
      password_hash = session.get('password_hash')
      salt = session.get('salt')
      data_dict[email] = {'messages':{},'salt':salt,'password_hash':password_hash}
      return redirect(url_for('send'))
    return render_template("activate.html",error='code did not match.please try again')

#end points for message passing/chat
@app.route("/send/",methods=['GET','POST'])
def send():
  if request.method=='GET':
    return render_template('send.html')
  elif request.method=='POST':
    #check if the mail is there in the data_dict
    email = request.form.get('email')
    if email in data_dict.keys():
      topic = request.form.get('topic')
      message = request.form.get('message')
      #generate random key for AES
      key = random_string()
      
      #encrypt the message and store it
      ciphertext= cryptocode.encrypt(message,key)
      #store the encrypted data
      encrypt_data = {'ciphertext':ciphertext}
      data_dict[email]['messages'][topic] = encrypt_data
      #send the email with key
      title = f'unlock key for :{topic}'
      mail_obj = Message(title, sender = app.config['MAIL_USERNAME'], recipients = [email])
      mail_obj.body = f'{key}'
      mail.send(mail_obj)
      return render_template('send.html',message='the message is sent')
    return render_template('send.html',message='the email is not registered')
      
 
@app.route("/msg/list/",methods=['GET'])
def msgs():
  if request.method=='GET':
    email = session.get('email')
    topics = data_dict[email]['messages'].keys()
    return render_template('topic_list.html',topics=topics)

@app.route("/msg/<string:topic>",methods=['GET','POST'])
def msg(topic):
  if request.method=='GET':
    return render_template('topic.html')
  elif request.method=='POST':
    email = session.get('email')
    msg = data_dict[email]['messages'][topic]
    print(msg)
    #decode message
    ciphertext = msg['ciphertext']
    key = request.form.get('key')
    plaintext = cryptocode.decrypt(ciphertext,key)
    #return decoded message
    return render_template('message.html',message=plaintext)
if __name__=='__main__':
  app.run(host='0.0.0.0',port=5000,debug=True)
    
