#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import webapp2
import jinja2

from google.appengine.api import users
import cgi
import json
import os
from pprint import pprint
from google.appengine.ext import ndb
from datetime import date 
import logging


import gdata
from apiclient import discovery
from oauth2client import appengine
from oauth2client import client
from google.appengine.api import memcache
import httplib2
import pickle


JINJA_ENVIRONMENT = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), '')))

logging.getLogger().setLevel(logging.DEBUG)

CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')
logging.info('CLIENT_SECRETS is ' + CLIENT_SECRETS)

http = httplib2.Http(memcache)
service = discovery.build("calendar", "v3", http=http)
decorator = appengine.oauth2decorator_from_clientsecrets(
    CLIENT_SECRETS,
    scope='https://www.google.com/calendar/feeds/',
    message='MISSING_CLIENT_SECRETS_MESSAGE')

logging.info("decorator.callback_path is %s" % decorator.callback_path)
logging.info("decorator.callback_handler() is %s" % decorator.callback_handler())


class Event(ndb.Model):
    eName = ndb.StringProperty()
    eLocation = ndb.StringProperty()
    eDate = ndb.DateProperty()
    eTime = ndb.StringProperty()
    eDetails = ndb.TextProperty()


class Helper():
    def __init__(self):
        pass

    @classmethod
    def getListDummy(cls,n):
        return [Event(eName="eName %d" % (i,), eDate=date(2013,9,20), eTime="1:00 PM - 4:00 PM", eLocation="UCS 305", eDetails="What courses in the Yale College Programs...") for i in xrange(0,n)]
    
    @classmethod
    def getListWeb(cls,n):
        pass
    
    @classmethod
    def getListNDB(cls,n):
        pass


class MainHandler(webapp2.RequestHandler):
    
    @decorator.oauth_required
    def get(self):
        http = decorator.http()


        # user = users.get_current_user()
        # if user:
        #     pass
        #     logging.info("user.nickname() is %s" % user.nickname())
        #     #self.response.out.write('Hello, ' + user.nickname())
        # else:
        #     self.redirect(users.create_login_url(self.request.uri))
        #     user = users.get_current_user()

        eventList = Helper.getListDummy(100)
        template_values = {
            'dict':{'a':"test",'b':'bb'},
            'eventList':eventList
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.out.write(template.render(template_values))

        
class AuthHandler(webapp2.RequestHandler):
    
    @decorator.oauth_aware
    def get(self):
        variables = {
            'url': decorator.authorize_url(),
            'has_credentials': decorator.has_credentials()
        }
        template = JINJA_ENVIRONMENT.get_template('grant.html')
        self.response.write(template.render(variables))


class GetAllEvents(webapp2.RequestHandler):
    
    def post(self):
        events = [{'eTime':'2013-aug-20','eName':'orientation'},{'eTime':'2013-aug-21','eName':'reg'}]
        jsonStr = json.dumps(events)
        self.response.out.write(jsonStr)

class AddToCalendar(webapp2.RequestHandler):
    
    def post(self):
        self.response.out.write('<html><body>You wrote:<pre>')
        self.response.out.write(cgi.escape(self.request.get('content')))
        self.response.out.write('</pre></body></html>')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/auth', AuthHandler),
    ('/add', AddToCalendar),
    ('/getallevents', GetAllEvents),
    (decorator.callback_path, decorator.callback_handler())
], debug=True)
