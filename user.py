
# coding: utf-8

# In[66]:

from flask import Flask, render_template, flash, request, url_for, redirect, session
from flask_wtf import Form
from wtforms import TextField, TextAreaField, SubmitField, validators, ValidationError, PasswordField, StringField
from wtforms import BooleanField
#from wtforms_alchemy import PhoneNumberField

#from forms import ContactForm, SignupForm
from flask_mail import Message, Mail
#from passlib.hash import sha256_crypt
#import escape-string as thwart
#import gc


# In[67]:

from flask import Flask

app = Flask(__name__)

app.secret_key = 'development key'

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = 'mgresap@gmail.com'      # 'contact@example.com'
app.config["MAIL_PASSWORD"] = 'wevxbgm1'               # 'your-password'


#from routes import mail
mail = Mail()

mail.init_app(app)

from flask_sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5432/audit'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ynmfoitwdrfufl:fcdc5a2eff67d02812cab4bda26e1bff1d4b050aa09b54c0b7c730ea93a5c0b5@ec2-54-221-255-153.compute-1.amazonaws.com:5432/d6rmmhfa7ijsat?sslmode=require'
#from models import db
db = SQLAlchemy()

# db.create_all()
# db.session.commit()

class User(db.Model):
    __tablename__ = 'users'
#     uid = db.Column(db.Integer)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    mobile = db.Column(db.Integer, primary_key = True)
    pwdhash = db.Column(db.String(54))

    def __init__(self, firstname, lastname, email, mobile, password):

        self.firstname = firstname.title()
        self.lastname = lastname.title()
        self.email = email.lower()
        self.mobile = mobile
        self.set_password(password)

    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

db.init_app(app)

#import app.routes


# In[68]:

class SignupForm(Form):

    firstname = StringField("First name",  [validators.DataRequired("Please enter your first name.")])
    lastname = StringField("Last name",  [validators.DataRequired("Please enter your last name.")])
    email = StringField("Email",  [validators.DataRequired("Please enter your email address."),
                                 validators.Email("Please enter your email address.")])
    #password = PasswordField('Password', [validators.Required("Please enter a password.")])
    mobile = StringField('Mobile', [validators.DataRequired(), validators.Length(min=8, max=8)])#country_code='SG', display_format='national')

    password = PasswordField('New Password', [validators.DataRequired("Please enter a password.")])#,
#                                               validators.EqualTo('confirm', message='Passwords must match')])
#     confirm = PasswordField('Repeat Password')
#     accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice (updated Jan 22, 2015)',
#                               [validators.DataRequired()])

    submit = SubmitField("Create account")


# class RegistrationForm(Form):
#     firstname = TextField("First name",  [validators.Required("Please enter your first name.")])
#     lastname = TextField("Last name",  [validators.Required("Please enter your last name.")])
#     email = TextField("Email address",  [validators.Required("Please enter your email address."),
#                                          validators.Email("Please enter your email address.")])
#     #username = TextField('Username', [validators.Length(min=4, max=20)])
#     #email = TextField('Email Address', [validators.Length(min=6, max=50)])
#     password = PasswordField('New Password', [validators.Required("Please enter a password."),
#                                               validators.EqualTo('confirm', message='Passwords must match')])
#     confirm = PasswordField('Repeat Password')
#     accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice (updated Jan 22, 2015)',
#                               [validators.Required()])
    #submit = SubmitField("Create account")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False

        user = User.query.filter_by(email = self.email.data.lower()).first()
        if user:
            self.email.errors.append("That email is already taken")
            return False
        else:
            return True


class SigninForm(Form):
    email = TextField("Email",  [validators.DataRequired("Please enter your email address."), validators.Email("Please enter your email address.")])
    password = PasswordField('Password', [validators.DataRequired("Please enter a password.")])
    submit = SubmitField("Sign In")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False

        user = User.query.filter_by(email = self.email.data.lower()).first()
        if user and user.check_password(self.password.data):
            return True
        else:
            self.email.errors.append("Invalid e-mail or password")
            return False


class ContactForm(Form):
    name = TextField("Name",  [validators.DataRequired("Please enter your name.")])
    email = TextField("Email",  [validators.DataRequired("Please enter your email address."), validators.Email("Please enter your email address.")])
    subject = TextField("Subject",  [validators.DataRequired("Please enter a subject.")])
    message = TextAreaField("Message",  [validators.DataRequired("Please enter a message.")])
    submit = SubmitField("Send")



# In[69]:

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('contact.html', form=form)
        else:
            msg = Message(form.subject.data, sender='mgresap@gmail.com', recipients=['lip_h@hotmail.com'])
            msg.body = """
            From: %s &lt;%s&gt;
            %s
            """ % (form.name.data, form.email.data, form.message.data)

            mail.send(msg)

            return 'Form posted.'

    elif request.method == 'GET':
        return render_template('contact.html', form=form)


# In[70]:

# from flask import Flask

# app = Flask(__name__)

#mail = Mail()
@app.route('/signup', methods=['GET', 'POST'])
def signup():

    form = SignupForm()

    if 'email' in session:
        return redirect(url_for('profile'))


    if request.method == 'POST':

        if form.validate() == False:

            return render_template('signup.html', form=form)
        else:

            newuser = User(form.firstname.data, form.lastname.data, form.email.data, form.mobile.data,
                           form.password.data)
            db.session.add(newuser)
            db.session.commit()
            session['email'] = newuser.email
#             return "[1] Create a new user [2] sign in the user [3] redirect to the user's profile"
            return redirect(url_for('profile'))
    else:
        return render_template('signup.html', form=form)


# In[71]:

#  url mapping for /profile

@app.route('/profile')
def profile():
    if 'email' not in session:
        return redirect(url_for('signin'))

    user = User.query.filter_by(email = session['email']).first()

    if user is None:
        return redirect(url_for('signin'))
    else:
        return render_template('profile.html')


# In[72]:

# url mapping for /signin

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SigninForm()

    if 'email' in session:
        return redirect(url_for('profile'))

    if request.method == 'POST':
        if form.validate() == False:
            return render_template('signin.html', form=form)
        else:
            session['email'] = form.email.data
            return redirect(url_for('profile'))

    elif request.method == 'GET':
        return render_template('signin.html', form=form)


# In[73]:

@app.route('/signout')
def signout():

  if 'email' not in session:
    return redirect(url_for('signin'))

  session.pop('email', None)
  return redirect(url_for('home'))


# In[ ]:




# In[27]:

# @app.route('/register/', methods=["GET","POST"])
# def register_page():
#     try:
#         form = RegistrationForm(request.form)

#         if request.method == "POST" and form.validate():
#             username  = form.username.data
#             email = form.email.data
#             password = sha256_crypt.encrypt((str(form.password.data)))
#             c, conn = connection()

#             x = c.execute("SELECT * FROM users WHERE username = (%s)",
#                           (thwart(username)))

#             if int(x) > 0:
#                 flash("That username is already taken, please choose another")
#                 return render_template('register.html', form=form)

#             else:
#                 c.execute("INSERT INTO users (username, password, email, tracking) VALUES (%s, %s, %s, %s)",
#                           (thwart(username), thwart(password), thwart(email), thwart("/introduction-to-python-programming/")))

#                 conn.commit()
#                 flash("Thanks for registering!")
#                 c.close()
#                 conn.close()
#                 gc.collect()

#                 session['logged_in'] = True
#                 session['username'] = username

#                 return redirect(url_for('dashboard'))

#         return render_template("register.html", form=form)

#     except Exception as e:
#         return(str(e))


# In[74]:

if __name__ == "__main__":
    app.run()


# In[ ]:
