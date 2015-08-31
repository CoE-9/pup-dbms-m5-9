import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb
import jinja2
import os
import logging
import json
import urllib

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
	return ndb.Key('Guestbook', guestbook_name)

class Thesis(ndb.Model):
	app_user = ndb.StringProperty(indexed=True)
	app_user_id = ndb.StringProperty(indexed=True)
	year = ndb.StringProperty(indexed=True)
	thesis_title = ndb.StringProperty(indexed=True)
	abstract = ndb.StringProperty(indexed=True)
	adviser = ndb.StringProperty(indexed=True)
	section = ndb.StringProperty(indexed=True)
	date = ndb.DateTimeProperty(auto_now_add=True)

class Student(ndb.Model):
	first_name = ndb.StringProperty(indexed=True)
	last_name = ndb.StringProperty(indexed=True)
	email = ndb.StringProperty(indexed=True)
	number = ndb.StringProperty()
	student_date = ndb.DateTimeProperty(auto_now_add=True)

class MainPageHandler(webapp2.RequestHandler):
    def get(self):

    	user = users.get_current_user()
    	url = users.create_logout_url(self.request.uri)
    	url_linktext = 'Logout'

    	template_data = {
    		'user': user,
    		'url': url,
    		'url_linktext': url_linktext
    	}

    	if user:
        	template = JINJA_ENVIRONMENT.get_template('main.html')
        	self.response.write(template.render(template_data))
        else:
        	self.redirect('login')

class ThesisCpE(webapp2.RequestHandler):
	 
	def get(self):
		thesis = Thesis.query().order(-Thesis.date).fetch()
		thesis_list = []

		for thesis in thesis:
			creator = thesis.app_user
			created_by = ndb.Key('Student',creator)
			thesis_list.append({
                    'id' : thesis.key.id(),
                    'Year' : thesis.year,
                    'Title' : thesis.thesis_title,
                    'Abstract' : thesis.abstract,
                    'Adviser' : thesis.adviser,
                    'Section' : thesis.section,
                    'app_user' : thesis.app_user,
                    'creator_fName' : created_by.get().first_name,
                    'creator_lName' : created_by.get().last_name
                })

		response = {
			'result' : 'OK',
			'data' : thesis_list
        }
		self.response.headers['Content-Type'] = 'application/json'
		self.response.out.write(json.dumps(response))

	def post(self):
		user = users.get_current_user()
		thesis = Thesis()
		thesis.year = self.request.get('year')
		thesis.thesis_title = self.request.get('thesis_title')
		thesis.abstract = self.request.get('abstract')
		thesis.adviser = self.request.get('adviser')
		thesis.section = self.request.get('section')
		thesis.app_user = user.nickname()
		thesis.app_user = user.user_id()
		thesis.put()

		creator = thesis.app_user
		created_by = ndb.Key('Student', creator)

		self.response.headers['Content-Type'] = 'application/json'
		response = {
		    'result' : 'OK',
		    'data': {
		        'id' : thesis.key.id(),
		            'year' : thesis.year,
		            'thesis_title' : thesis.thesis_title,
		            'abstract' : thesis.abstract,
		            'adviser' : thesis.adviser,
		            'section' : thesis.section,
		            'app_user' : thesis.app_user,
		            'creator_fName' : created_by.get().first_name,
                    'creator_lName' : created_by.get().last_name
		    }
		}
		self.response.out.write(json.dumps(response))

class Login(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		template_data = {
			'login' : users.create_login_url(self.request.uri),
			'register' : users.create_login_url(self.request.uri)
		}
		if user:
			self.redirect('api/user')
		else:
			template = JINJA_ENVIRONMENT.get_template('login.html')
			self.response.write(template.render(template_data))

class Register(webapp2.RequestHandler):
	def get(self):
		user_login = users.get_current_user()

		if user_login:
			user_key = ndb.Key('Student', user_login.user_id())
			user = user_key.get()
			if user:
				self.redirect('/')
			else:
				template = JINJA_ENVIRONMENT.get_template('register.html')
				logout_url = users.create_logout_url('/login')
				template_data = {
					'logout_url' : logout_url
				}
				self.response.write(template.render(template_data))
				template_data
		else:
			login_url = users.create_login_url('/api/user')
			self.redirect(login_url)

	def post(self):
		user_login = users.get_current_user()
		fName = self.request.get('first_name')
		lName = self.request.get('last_name')
		num = self.request.get('number')
		email = user_login.email()
		user_id = user_login.user_id()
		user = Student(id=user_id, first_name=fName, last_name=lName, email=email, number=num)
		user.put()

		self.response.headers['Content-Type'] = 'application/json'
		response = {
			'result' : 'OK'
		}
		self.response.out.write(json.dumps(response))
		self.redirect('/')

class DeleteInfo(webapp2.RequestHandler):
    def get(self, studentId):
        d = Thesis.get_by_id(int(studentId))
        d.key.delete()
        self.redirect('/')

app = webapp2.WSGIApplication([
('/api/thesis', ThesisCpE),
('/login', Login),
('/api/user', Register),
('/thesis/delete/(.*)', DeleteInfo),
('/home', MainPageHandler),
('/', MainPageHandler)
], debug=True)