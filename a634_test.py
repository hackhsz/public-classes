import os
import a634
import unittest

from a634 import basedir
from a634 import app, db
from a634 import Class,Skill,User,Mages,RegistrationForm
import pdb




class A634TestCase(unittest.TestCase):
    
    def setUp(self):
        app.config['TESTING'] = True
      #  app.config["SQLALCHEMY_DATABASE_URI"] =  'postgresql://'+ os.path.join(basedir, 'hushizh_testdb')  
        app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/hushizh_testdb" 
        self.app = a634.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


    def test_make_image(self):  
             #user = User(email=form.email.data,username=form.username.data,password=form.password.data)
        newa  = Mages(name="bob")
        db.session.add(newa)
        db.session.commit()
        thisclass = Mages.query.filter_by(name="bob").first()
        self.assertEqual(thisclass.name,newa.name)

    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)


    def test_home_status_type(self):

        result = self.app.get('/') 
        self.assertFalse(b'<form>' in result.data)
        #self.assertTemplateUsed('index.html')
      
    def test_classes_skills_type(self):

        newskill =Skill(name="organizing bed",level="L")

        badskill = Skill(name="do not want to do", level="M")
        new1= Class(class_number=388)

        new2 = Class(class_number=422)

        new1.skill.append(newskill)

        new2.skill.append(badskill)


        self.assertEqual(str(type(new1.skill)),"<class 'sqlalchemy.orm.dynamic.AppenderBaseQuery'>")


    def test_classes_skills(self):

        
        newskill =Skill(name="organizing bed",level="L")

        badskill = Skill(name="do not want to do", level="M")
        
        new1= Class(class_number=388)

        new2 = Class(class_number=422)

        new1.skill.append(newskill)

        new2.skill.append(badskill)

        self.assertNotEqual(new2.skill,new1.skill)


    def register(self, email, password, confirm):
        return self.app.post(
        '/register',
        data=dict(email=email, password=password, confirm=confirm),
        follow_redirects=True
        )

    def login(self, email, password):
        return self.app.post(
        '/login',
        data=dict(email=email, password=password),
        follow_redirects=True
        )



    def test_valid_user_registration(self):
        response = self.register('h@hcom.com', 'FlaskIsAwesome', 'FlaskIsAwesome')
        self.assertEqual(response.status_code, 200)
        #pdb.set_trace()
        #print(response.data)
        self.assertIn(b'You are now logged in', response.data)

    def test_invalid_user_registration_different_passwords(self):
        response = self.register('patkennedy79@gmail.com', 'FlaskIsAwesome', 'FlaskIsNotAwesome')
        self.assertIn(b'Are you a new User?', response.data)
      #  self.assertIn(b'Field must be equal to password.', response.data)


    def test_login_index(self):
        tester = app.test_client(self)
        response = tester.get('/login', content_type='html/text')
        self.assertEqual(response.status_code, 200)











if __name__ == "__main__":
    unittest.main(verbosity=2)
