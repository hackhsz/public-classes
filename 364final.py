import os
from flask import Flask,render_template, session, redirect, url_for, flash
from flask_wtf import FlaskForm
from flask_script import Manager, Shell
from wtforms import StringField, SubmitField,FileField, PasswordField, BooleanField, SelectMultipleField, ValidationError,IntegerField

from wtforms.validators import Required,Length,Email,Regexp,EqualTo
from flask_sqlalchemy import SQLAlchemy
import pdb
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message

basedir=os.path.abspath(os.path.dirname(__file__))

app=Flask(__name__)
app.debug= True
app.static_folder='static'
app.config['SECRET_KEY']='thisisaveryhardkeytofindbecauseitiscreatedbyme'
app.config["SQLALCHEMY_DATABASE_URI"]=os.environ.get('DATABASE_URL') or "postgresql://localhost/hushizhfinal"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



manager = Manager(app)
db = SQLAlchemy(app)
migrate=Migrate(app,db)
manager.add_command('db',MigrateCommand)
mail=Mail(app)

def make_shell_context():
    return dict(app=app,db=db,Class=Class,Skill=Skill,Level=Level)


manager.add_command("shell",Shell(make_context=make_shell_context))

collections = db.Table('collections',db.Column('skill_id',db.Integer,db.ForeignKey('skill.id')),db.Column('class_id',db.Integer,db.ForeignKey('class.id')))




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
    

    def __repr__(self):
        return "This class is {}".format(self.class_name)



class Skill(db.Model):
    __tablename__="skill"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(300),unique=True)
    level = db.Column(db.String(500))
    skillsections_id = db.Column(db.Integer,db.ForeignKey("skillsections.id"))
    #class = db.relationship('Class',secondary = collections,backref=db.backref('skill',lazy='dynamic'),lazy='dynamic')

    def __repr__(self):
        return "This skill is {}".format(self.name)


class SkillForm(FlaskForm):
    skill_name = StringField("What is the skill name of this",validators=[Required()])
    level = StringField("What is the level of this skill",validators=[Required()])
    section_name=StringField("Nname of this class?", validators=[Required()])
    
    submit=SubmitField("Submit this Skill")

class ClassForm(FlaskForm):
#    skills= Skill.query.all()
    
    #all_skill_name = [(eachs.skill_name,l) for eachs in skills for l in levels]
    class_name=StringField("Nname of this class?", validators=[Required()])
    class_number=IntegerField("What is the class number?", validators=[Required()])

    #class_skill_picks= SelectMultipleField('Skills to include',choices=skills)
    
    #skill_section=StringField("name of this skillsection?",validators=[Required()])
    #skill_section_picks = SelectMultipleField('Skills for this section',choices=all_skill_name)
    submit= SubmitField('Submit')







def get_or_create_skillsection(db_session,section_name):
    skillsection = db.session.query(Skillsection).filter_by(name=section_name).first()
    if skillsection:
        return skillsection
    else:
        skill_sec = Skillsection(name=section_name)
        db_session.add(skill_sec)
        db_session.commit()
        return skill_sec


def get_skill_by_name(skill_name):
    skill = Skill.query.filter_by(name=skill_name).first()
    return skill

def get_or_create_skill(db_session,skill_name,lev,skillsectionname=[]):
    skill = db.session.query(Skill).filter_by(name=skill_name).first()
    if skill:
        return skill
    else:
        #new_section = get_or_create_skillsection(db_session,skillsectionname)
        newskill=Skill(name=skill_name,level=lev)
        for item in list_of_class:
            newitem = get_or_create_skillsection(db_session,item)
            newskill.skillsections.append(newitem)

        db_session.add(newskill)
        db_session.commit()
        return newskill

def get_or_create_class(db_session,class_num,list_of_skills):
   newclass= db_session.query(Class).filter_by(class_number=class_num).first()
   if newclass:
       return newclass
   else:
       newclass = Class(class_number=class_num)
       for item in list_of_skills:
           newclass.skill.append(item)
       db_session.add(newclass)
       db_session.commmit(newclass)
       return newclass





@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/',methods=['GET','POST'])
def index():
    form = SkillForm()
    skills = Skill.query.all()
    length_skills = len(skills)
    
    if form.validate_on_submit():
        if db.session.query(Skill).filter_by(name=form.skill_name.data).first():
            flash("you have this skill already")
        else:
            newlist=[]
            for item in list(form.section_name.data.split(",")):
                newlist.append(item.strip("#"))
            get_or_create_skill(db.session,form.skill_name.data,form.level.data,newlist)
        return redirect(url_for('see_all_skills'))
    return render_template('index.html',form=form,num_skills=length_skills)


@app.route('/all_skills')
def see_all_skills():
    all_skills=[]
    skills = Skill.query.all()
    for skill in skills:
        skillsec = Skillsection.query.filter_by(id=skill.skillsections_id).first()
        all_skills.append((skill.name,skillsec.name))
    return render_template('all_skills.html',all_skills=all_skills)


@app.route('/create_class_skills',methods=["GET","POST"])
def create_class_skills():
    form = ClassForm()
    if form.validate_on_submit():
        class_name = form.class_name.data
        class_num = form.class_number.data
        skills_data  = form.class_skill_picks.data
        skills_obj = [get_skill_by_name(item) for item in skills_data]
        
        get_or_create_class(db.ssession,class_num,skills_obj)
        return redirect(url_for('index'))
    return render_template('create_playlist.html',form=form)
        
      











if __name__ == '__main__':
    db.create_all()
    manager.run()
