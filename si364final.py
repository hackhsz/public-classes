# SI364- Final


import os
from flask import Flask,render_template, session, redirect, url_for, flash
from flask_wtf import FlaskForm
from flask_script import Manager, Shell
from wtforms import StringField, SubmitField
from wtforms.validator import Required
from flask_sqlalchemy import SQLAlchemy
import pdb

basedir=os.path.abspath(os.path.dirname(__file__))

app=Flask(__name__)
app.debug= True
app.config['SECRET_KEY']='thisisaveryhardkeytofindbecauseitiscreatedbyme'
app.config["SQLALCHEMY_DATABASE_URI"]="postgresql://localhost/hushizhfinal"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.static_folder='static'


manager = Manager(app)
db = SQLALchemy(app)
migrate=Migrate(app,db)
manager.add_command('db',MigrateCommand)
mail=Mail(app)

def make_shell_context():
    return dict(app=app,db=db,Class=Class,Skill=Skill,Level=Level)


manager.add_command("shell",Shell(make_context=make_shell_context))


class Association(db.Model):
    __tablename__ = "association"
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'),primary_key=True)
    skill_id = db.Column(db.Integer,db.ForeignKey('skill.id'),primary_key=True)
    level = db.Column(db.String(64),db.ForeignKey("level.level_name"))


class Class(db.Model):
    __tablename__="class"
    id = db.Column(db.Column(db.Integer,primary_key=True))
    class_name = db.Column(db.String(200),unique=True))
    class_number =db.Column(db.Integer,unique=True)
    skills = db.relationship('Skill',secondary = association,backref=db.backref('class',lazy='dynamic'),lazy='dynamic')

    def __repr__(self):
        return "This class is {}".format(self.class_name)


class Skill(db.Model):
    __tablename__="skill"
    id=db.Column(db.Integer,primary_key=True)
    skill_name=db.Column(db.String(200),unique=True)
    

    def __repr__(self):
        return "This skill is {} which belongs to {}".format(self.skill_name,self.class_name)


class Level(db.Model):
    __tablename__="level"
    id=db.Column(db.Integer.primary_key=True)
    level_name=db.Column(db.String(64))
    

    def __repr__(self):
        return "this level is {}".format(self.level_name)




class SkillForm(FlaskForm):
    skill_name = StringField("What is the skill name of this",validators=[Required()])
    submit=SubmitFiled("Submit this Skill")

class ClassForm(FlaskForm):
    skills= Skill.query.all()
    levels=['M','C','A',"L"]
    all_skill_name = [(eachs.skill_name,l) for eachs in skills for l in levels]
    class_name=StringField("Nname of this class?", validators=[Required()])
    class_number=IntegerField("What is the class number?", validators=[Required()])
    skill_picks= SelectMultipleField('Skills to include',choices=all_skill_name)
    submit= SubmitField('Submit')




def get_or_create_skill(db.session,skill_nam):
    skill = db_session.query(Skill).filter_by(skill_name=skill_nam).first()
    if skill:
        return skill
    else:
        skill=Class(class_name=class_nam)
        db_session.add(class)
        db_session.commit()
        return class
    
        
                
