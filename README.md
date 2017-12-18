# public-classes
Application Description:

Data Relationship:
     Skillsection:Skill One:Many
     Skill: Class: Many:Many

     This is an app links the skills with skillsection and classes. Skill sections house skills. For example, 
     "UX Engineering" is a skill section which may have skills such as "HTML","CSS" and other skills.
     Class can have many skills outcomes and skills can be mapped to different classes. Because there is no necessailry relationship between classes and skillsections, classes do not have skillsection_id. Only authorized user can create class with skills (persumplively instructors and faculties)

     One View to create Class: go to '/create_class'
     View to Upload: go to '/upload'


Please Note:
      1. I used template inheritance instead of flask email for the extension part
      2. The images are saved into images table which you could query out in command line
      3. To run actual file, please create a database called "hushizhfinal4"
      4. export FLASK_APP=a634.py  | python -m flask run
      5. To test, please create a database called "hushizh_testdb" on local to use the test
      6. To run test, type: python a634_test.py 
      7. Heroku Address: https://git.heroku.com/a634.git
      8. The screen shots of being added to database are under folder called "Adding_To_The_Tables
      9. Things need to be installed are at requirements.txt
      9. Enjoy!

