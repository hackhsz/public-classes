__author__="Shizhong Hu"




import os
from flask import Flask, render_template, session, redirect, request, url_for, flash
from flask_script import Manager, Shell
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, PasswordField, BooleanField, SelectMultipleField, ValidationError,IntegerField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from flask_sqlalchemy import SQLAlchemy
import random
from flask_migrate import Migrate, MigrateCommand
import pdb
# Imports for email from app
from flask_mail import Mail, Message
from threading import Thread
from werkzeug import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import requests
# Imports for login management
from flask_login import LoginManager, login_required, logout_user, login_user, UserMixin, current_user
import json



# Configure base directory of app
basedir = os.path.abspath(os.path.dirname(__file__))

# Application configurations
app = Flask(__name__)
app.static_folder = 'static'
app.config['SECRET_KEY'] = 'hardtoguessstring'
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL') or "postgresql://localhost/hushizhfinal4"  # TODO: decide what your new database name will be, and create it in postgresql, before running this new application
# Lines for db setup so it will work as expected
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set up email config stuff
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587 #default
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') # TODO export to your environs -- may want a new account just for this. It's expecting gmail, not umich
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_SUBJECT_PREFIX'] = '[Songs App]'
app.config['MAIL_SENDER'] = 'Admin <>' # TODO fill in email
app.config['ADMIN'] = os.environ.get('ADMIN') or "admin@example.com" # If Admin in environ variable / in prod or this fake email
app.config['HEROKU_ON'] = os.environ.get('HEROKU')

# Set up Flask debug and necessary additions to app
manager = Manager(app)
db = SQLAlchemy(app) # For database use
migrate = Migrate(app, db) # For database use/updating
manager.add_command('db', MigrateCommand) # Add migrate command to manager
mail = Mail(app) # For email sending

# Login configurations setup
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app)



def make_shell_context():
    return dict( app=app, db=db, Classes=Class,Skill=Skill,User=User)
# Add function use to manager
manager.add_command("shell", Shell(make_context=make_shell_context))


collections = db.Table('collections',db.Column('skill_id',db.Integer,db.ForeignKey('skill.id')),db.Column('class_id',db.Integer,db.ForeignKey('class.id')))


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    class_collections = db.relationship('Class',backref='User')
    #playlists = db.relationship('Playlist', backref='User')
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)












class Skillsection(db.Model):
    __tablename__="skillsections"
    id=db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(500))
    skills = db.relationship('Skill',backref='Skillsection')


    def __repr(self):
        return "This skillsection has a name {}".format(self.name)




class Class(db.Model):
    __tablename__="class"
    id = db.Column(db.Integer,primary_key=True)
   # class_name = db.Column(db.String(200),unique=True))                        
    class_number =db.Column(db.Integer,unique=True)
    skill = db.relationship('Skill',secondary = collections,backref=db.backref('class',lazy='dynamic'),lazy='dynamic')
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"))

    def __repr__(self):
        return "This class is {}".format(self.class_name)



class Skill(db.Model):
    __tablename__="skill"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(300),unique=True)
    level = db.Column(db.String(500))
    skillsections_id = db.Column(db.Integer,db.ForeignKey("skillsections.id"))
                                

    def __repr__(self):
        return "This skill is {}".format(self.name)

class SkillForm(FlaskForm):
    skill_name = StringField("What is the skill name of this",validators=[Required()])
    level = StringField("What is the level of this skill",validators=[Required()])
    section_name=StringField("Name of this class?")

    submit=SubmitField("Submit this Skill")


class ClassForm(FlaskForm):
    skill_picks =SelectMultipleField("skills to include")                                         
    class_name=StringField("Nname of this class?", validators=[Required()])
    class_number=IntegerField("What is the class number?", validators=[Required()])

                                                             
    submit= SubmitField('Submit')



## DB load functions
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) # returns User object or None


##### Set up Forms #####

class RegistrationForm(FlaskForm):
    email = StringField('Email:', validators=[Required(),Length(1,64),Email()])
    username = StringField('Username:',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Usernames must have only letters, numbers, dots or underscores')])
    password = PasswordField('Password:',validators=[Required(),EqualTo('password2',message="Passwords must match")])
    password2 = PasswordField("Confirm Password:",validators=[Required()])
    submit = SubmitField('Register User')

    #Additional checking methods for the form
 #   def validate_email(self,field):
  #      if User.query.filter_by(email=field.data).first():
   #         raise ValidationError('Email already registered.')

   # def validate_username(self,field):
    #    if User.query.filter_by(username=field.data).first():
     #       raise ValidationError('Username already taken')

class LoginForm(FlaskForm):
    email = StringField('Email as Your Login', validators=[Required(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Please Keep me logged in')
    submit = SubmitField('Log In')










def get_or_create_skillsection(db_session,section_name):
    skillsection = db.session.query(Skillsection).filter_by(name=section_name).first()
    if skillsection:
        return skillsection
    else:
        skill_sec = Skillsection(name=section_name)
        db_session.add(skill_sec)
        db_session.commit()
        return skill_sec

def get_skill_by_id(sid):
    skill = Skill.query.filter_by(id=sid).first()
    return skill



def get_skill_by_name(skill_name):
    skill = Skill.query.filter_by(name=skill_name).first()
    return skill

def get_or_create_skill(db_session,skill_name,lev,skillsectionname=[]):
    skill = db.session.query(Skill).filter_by(name=skill_name).first()
    if skill:
        return skill
    else:  
        newskill=Skill(name=skill_name,level=lev)
        for item in skillsectionname:
            newitem = get_or_create_skillsection(db_session,item)
            newskill.skillsections_id=newitem.id

        db_session.add(newskill)
        db_session.commit()
        return newskill

def get_or_create_class(db_session,class_num,list_of_skills,this_user):
   newclass= db_session.query(Class).filter_by(class_number=class_num,user_id=this_user.id).first()
   if newclass:
       return newclass
   else:
       newclass = Class(class_number=class_num,user_id=this_user.id)
       for item in list_of_skills:
           newclass.skill.append(item)
       db_session.add(newclass)
       db_session.commit()
       return newclass



@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500









@app.route('/login',methods=["GET","POST"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            return redirect(request.args.get('next') or url_for('index'))
        flash('Invalid username or password.')
    return render_template('login.html',form=form)




@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("you are now logged out")
    return redirect(url_for('index'))

@app.route('/register',methods=["GET","POST"])
def register():
    form = RegistrationForm()
    users=User.query.all()
    if request.method == "POST":
        
        user = User(email=form.email.data,username=form.username.data,password=form.password.data)
        if User.query.filter_by(email=form.email.data).first():
            flash("This email existed before")
            return redirect(url_for('login'))
        if User.query.filter_by(username=form.username.data).first():
            flash("This username existed before")
            return redirect(url_for('login'))

#        user = User(email=form.email.data,username=form.username.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("You are now logged in")
        return redirect(url_for('login'))
    return render_template('register.html',form=form)













@app.route('/test')
@login_required

def test1():
    return "This is a test"



@app.route('/',methods=['GET','POST'])
def index():
    form = SkillForm()
    skills = Skill.query.all()
    length_skills = len(skills)
    if request.method == 'POST':
        if db.session.query(Skill).filter_by(name=form.skill_name.data).first():
            flash("you have this skill already")
        else:
            newlist=[]
            for item in list(form.section_name.data.split(",")):
                newlist.append(item.strip("#"))
            temp=get_or_create_skill(db.session,form.skill_name.data,form.level.data,newlist)
            
        return redirect(url_for('see_all_skills'))
    return render_template('index.html',form=form,num_skills=length_skills)


@app.route('/all_skills')
def see_all_skills():
    all_skills=[]
    form = SkillForm()
    skills = Skill.query.all()
    for skill in skills:
        skillsec = Skillsection.query.filter_by(id=skill.skillsections_id).first()
        all_skills.append((skill.name,skillsec.name))
    return render_template('all_skills.html',all_skills=all_skills,form=form)


@app.route('/create_class',methods=["GET","POST"])
@login_required
def create_class_list():
    form=ClassForm()
    choice=[]
    for skill in Skill.query.all():
        choice.append((skill.id,skill.name))
    form.skill_picks.choices = choice
    if request.method == 'POST':
        selected = form.skill_picks.data
        skill_objects = [get_skill_by_id(int(id)) for id in selected]
        get_or_create_class(db.session,class_num=form.class_number.data,list_of_skills=skill_objects,this_user=current_user)
        class_str="si "+str(form.class_number.data) 
        temp1=str(form.class_number.data)
       
        return render_template('thisclass.html',class_num=temp1)
    return render_template('class_list.html',form=form)




@app.route('/classview/<fclass>')
def check_this_class(fclass):
    class_str="si "+fclass
#    pdb.set_trace()
    print(class_str)
    baseURL = "https://www.googleapis.com/customsearch/v1?"
    parameters={}

#        temp1=str(form.class_number.data)
    parameters['cx']="016464920041578697449:vwctkt8voqy"
    parameters['key']="AIzaSyA2ELo-AwOO100dKFhbtKdk5e1E93h3HcU"
    parameters['q']=class_str
    response = requests.get(baseURL,params=parameters)
    repsonsew = json.loads(response.text)
    newlist=[]
    for i in range(0,4):
        newlist.append((repsonsew["items"][i]["snippet"][0:200],repsonsew["items"][i]['pagemap']['metatags'][0]["twitter:url"]))
    return render_template('class_info.html',data=newlist)
    

    


if __name__ == '__main__':
    db.create_all()
    manager.run()













