#!/usr/bin/env python

"""
conference.py -- Udacity conference server-side Python App Engine API;
    uses Google Cloud Endpoints

$Id: conference.py,v 1.25 2014/05/24 23:42:19 wesc Exp wesc $

created by wesc on 2014 apr 21

"""

__author__ = 'wesc+api@google.com (Wesley Chun)'


from datetime import datetime

import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from google.appengine.ext import ndb

from models import Profile
from models import ProfileMiniForm
from models import ProfileForm

from models import Hangout
from models import HangoutForm

from settings import WEB_CLIENT_ID
from settings import ANDROID_CLIENT_ID
from settings import IOS_CLIENT_ID
from settings import ANDROID_AUDIENCE

from utils import getUserId

import json

EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID
MEMCACHE_ANNOUNCEMENTS_KEY = "RECENT_ANNOUNCEMENTS"
ANNOUNCEMENT_TPL = ('Last chance to attend! The following conferences '
                    'are nearly sold out: %s')
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

@endpoints.api(name='conference', version='v1', audiences=[ANDROID_AUDIENCE],
    allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID, ANDROID_CLIENT_ID, IOS_CLIENT_ID],
    scopes=[EMAIL_SCOPE])
class ConferenceApi(remote.Service):
    """Conference API v0.1"""

# - - - Profile objects - - - - - - - - - - - - - - - - - - -

    def _copyProfileToForm(self, prof):
        """Copy relevant fields from Profile to ProfileForm."""
        # copy relevant fields from Profile to ProfileForm
        pf = ProfileForm()
        for field in pf.all_fields():
            if hasattr(prof, field.name):
                setattr(pf, field.name, getattr(prof, field.name))

        pf.check_initialized()
        return pf


    def _getProfileFromUser(self):
        """Return user Profile from datastore, creating new one if non-existent."""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        # get Profile from datastore

        user_id = getUserId(user)
        p_key = ndb.Key(Profile, user_id)
        profile = p_key.get()
        # create new Profile if not there
        if not profile:
            profile = Profile(
                key = p_key,
                displayName = user.nickname(),
                mainEmail= user.email()
            )
            profile.put()

        return profile      # return Profile


    def _doProfile(self, save_request=None):
        """Get user Profile and return to user, possibly updating it first."""
        # get user Profile
        prof = self._getProfileFromUser()

        # if saveProfile(), process user-modifyable fields
        if save_request:
            for field in ('displayName'):
                if hasattr(save_request, field):
                    val = getattr(save_request, field)
                    if val:
                        setattr(prof, field, str(val))
                        #if field == 'teeShirtSize':
                        #    setattr(prof, field, str(val).upper())
                        #else:
                        #    setattr(prof, field, val)
                        prof.put()

        # return ProfileForm
        return self._copyProfileToForm(prof)


    @endpoints.method(message_types.VoidMessage, ProfileForm,
            path='profile', http_method='GET', name='getProfile')
    def getProfile(self, request):
        """Return user profile."""
        return self._doProfile()


    @endpoints.method(ProfileMiniForm, ProfileForm,
            path='profile', http_method='POST', name='saveProfile')
    def saveProfile(self, request):
        """Update & return user profile."""
        return self._doProfile(request)

# - - - Hangout - - - - - - - - - - - - - - - - - - - - - - - 
    @endpoints.method(HangoutForm, HangoutForm, 
            path='createHangout', 
            http_method='POST', name='createHangout')
    def createHangout(self, request):
        #initialize key datapoints here

        #getUserInformationHere
        user = endpoints.get_current_user()
        print user
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)
        p_key = ndb.Key(Profile, user_id)

        #Save informatoin from html forms to Hangout Database.
        data = {field.name: getattr(request, field.name) for field in request.all_fields()}
        print data

        #add in the the current time and date when event is created.
        data['dateEventCreated'] = datetime.utcnow()

        #convert form dates to DateTimeProperties
        data['date1'] = datetime.strptime(data['date1'][:10], "%Y-%m-%d").date()
        data['date2'] = datetime.strptime(data['date2'][:10], "%Y-%m-%d").date()
        data['date3'] = datetime.strptime(data['date3'][:10], "%Y-%m-%d").date()
        data['deadlineDate'] = datetime.strptime(data['deadlineDate'][:10], "%Y-%m-%d").date()
        
        print data
        #FriendListHandling
        #manage creating a dictionary for friendList is appropriate default info. Check the model.        
        #name, key, voteRank, confirmationiffirstchoicenotpicked
        #Add the keys of all the users to the friendList dictionary.

        ####NOT MANDATORY, BUT WOULD IMPLEMENT HERE
        #Don't know how to implement yet, but account for those users not registered.

        #update User's Profiles
        #add the eventKey to all users associated with the hangout

        #place into the database
        #Hangout(**data).put()

        return request

    @endpoints.method(message_types.VoidMessage, message_types.VoidMessage, 
            path='getAllHangouts', 
            http_method='GET', name='getAllHangouts')
    def getAllHangouts(self, request):
        print "here bitch!!!"
        #Query the database Hangout.get()
        #put that into the form for showcasing everything, create the model

        return request

    #def invited():
    #    pass

    #def votedWaiting():
    #   pass

    #def done():
    #   pass

api = endpoints.api_server([ConferenceApi]) # register API

#Sample Code to help me out. Reminder Code
    #data = Hangout.query()
    #for p in data:
    #    print p.key.id()
    #    print p.key.urlsafe()
    #Profile.Query(current user)
    #then query more to get the list of objects 
    #p = Hangout.query().order(Hangout.date1)
    #    for x in p:
    #        print x.date1