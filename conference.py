#!/usr/bin/env python

"""
conference.py -- Udacity conference server-side Python App Engine API;
    uses Google Cloud Endpoints

$Id: conference.py,v 1.25 2014/05/24 23:42:19 wesc Exp wesc $

created by wesc on 2014 apr 21

"""

__author__ = 'wesc+api@google.com (Wesley Chun)'


from datetime import datetime
import time

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
from models import HangoutForms
from models import EmailRegFormInput

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


    ####Registration and Login Codes:
    @endpoints.method(EmailRegFormInput, EmailRegFormInput,
            path='emailRegistration', http_method='POST', name='emailRegistration')
    def emailRegistration(self, request):
        #Get and save the email here.
        #Add the old code in here.
        print request

        return request


# - - - Hangout - - - - - - - - - - - - - - - - - - - - - - - 
    def _copyHangoutToForm(self, hangout):
        hang = HangoutForm()
        for field in hang.all_fields():
            if hasattr(hangout, field.name):
                if field.name in ('date1', 'date2', 'date3', 'time1', 'time2', 'time3', 'deadlineDate',\
                 'deadlineTime', 'dateEventCreated', 'totalCounter', 'partyTotal', 'votingCompleted'):
                    setattr(hang, field.name, str(getattr(hangout, field.name)))
                else:
                    setattr(hang, field.name, getattr(hangout, field.name))
        hang.check_initialized()
        return hang

    @endpoints.method(HangoutForm, HangoutForm, 
            path='createHangout', 
            http_method='POST', name='createHangout')
    def createHangout(self, request):
        #initialize key datapoints here

        #getUserInformationHere
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)
        p_key = ndb.Key(Profile, user_id)

        #Save information from html forms to Hangout Database.
        data = {field.name: getattr(request, field.name) for field in request.all_fields()}

        #add in the the current time and date when event is created.
        data['dateEventCreated'] = datetime.utcnow()

        #Handle Dates
        data['date1'] = datetime.strptime(data['date1'], "%Y-%m-%d").date()
        data['date2'] = datetime.strptime(data['date2'], "%Y-%m-%d").date()
        data['date3'] = datetime.strptime(data['date3'], "%Y-%m-%d").date()

        #Handle Times
        data['time1'] = datetime.strptime(data['time1'], "%H:%M").time()
        data['time2'] = datetime.strptime(data['time2'], "%H:%M").time()
        data['time3'] = datetime.strptime(data['time3'], "%H:%M").time()

        #Handle deadlineDate
        data['deadlineDate'] = datetime.strptime(data['deadlineDate'], "%Y-%m-%d").date()
        #Handle deadlineTime
        data['deadlineTime'] = datetime.strptime(data['deadlineTime'], "%H:%M").time()

        #FriendListHandling
        #manage creating a dictionary for friendList is appropriate default info. Check the model.        
        #name, key, voteRank, confirmationiffirstchoicenotpicked
        #Add the keys of all the users to the friendList dictionary.
        friendHandler=[]
        friendsInJson=json.loads(data['friendList'])
        counter=0
        
        #I should really pass the friendID not just the name. Be sure to switch this
        #later in production
        for friend in friendsInJson:
            if friend == None:
                pass
            else:
                #I have to get check the user's profileID here and do a database query of somesort.
                p ={"profileID" : 0, "voteRank" : [0,0,0], "firstChoie" : 0, "confirmation" :0}
                z ={friend : p}
                friendsInJson[counter] = z
                counter=counter+1

                #then I have to get the friend's id (like I do with my own username
                #thenquery their profile
                #then just add them to the list of id's as I need to finish creating this event first
                #friendID list*******
                #proceed to after saving to the hangout below

        #Handle in this area, those that are not found within our system

        #Add a count for the event creator        
        counter = counter + 1
        data['friendList'] = json.dumps(friendsInJson)

        ###Add Event Creator 
        data['eventCreator'] = str(user_id)

        #process the user's own voting preferences
        data['groupVoteRanks'] = json.dumps({user_id : data['groupVoteRanks']})

        ####Add the Total Party Count
        data['totalCounter'] = 0
        ####Add the Party Total
        data['partyTotal'] = counter
        ###Initialize the Rankings
        data['finalResults'] = json.dumps([0,0,0])
        ###Voting Completed
        data['votingCompleted'] = False

        ####NOT MANDATORY, BUT WOULD IMPLEMENT HERE
        #Don't know how to implement yet, but account for those users not registered.

        #place into the database
        Hangout(**data).put()
        #wait for it to generate the keys
        time.sleep(.1)
        #Query the keys for the hangout
        #Make sure that the query brings back this unique event. I have to figure out
        #how to guarantee that this event is unique or that the search query is unique
        #Maybe this is where the parent ancestors come into play?
        hangoutQry = Hangout.query(Hangout.eventCreator == str(user_id), Hangout.dateEventCreated == data['dateEventCreated'])
        #add the eventKey to all users associated with the hangout

        #UPDATING THE EVENT CREATOR WITH THE APPriate hangout keys
        #update User's Profiles
        creator = p_key.get()
        #get the list of events that the user is waiting on
        if creator.eventsWaitingOn == None:
            eventsWaitingOn = []
        else:
            eventsWaitingOn=json.loads(creator.eventsWaitingOn)

        for event in hangoutQry:
            eventKey = event.key.id()
            eventsWaitingOn.append(eventKey)
            creator.eventsWaitingOn = json.dumps(eventsWaitingOn)
            #generates an L when appended to a list. I don't know why. but just printing it out, it is as advertised
        creator.put()

        #####Update the friends that were invited with the hangout key as well
        #update down here
        #get the friendid list created up above
        #emulate what I did for the event creator just above but place in eventsInvited

        return request

    @endpoints.method(message_types.VoidMessage, message_types.VoidMessage, 
            path='getAllHangouts', 
            http_method='GET', name='getAllHangouts')
    def getAllHangouts(self, request):
        print "here bitch!!!"
        #Query the database Hangout.get()
        #put that into the form for showcasing everything, create the model

        return request

    @endpoints.method(message_types.VoidMessage, HangoutForms, 
        path='invited', 
        http_method='GET', name='invited')
    def invited(self, request):
        #How do you know you are invited?
        #check your invited queue on your profile. Should have been handled during event creation
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)
        p_key = ndb.Key(Profile, user_id)
        userData=p_key.get()
        
        
        #handle the string processing
        eventsInvited = json.loads(userData.eventsInvited)
        eventList=[]
        form = HangoutForm()
        for eventId in eventsInvited:
            #get the event from ndb
            event = ndb.Key(Hangout, eventId).get()

            eventList.append(event)

        return HangoutForms(items=[self._copyHangoutToForm(hangout) for hangout in eventList]

    @endpoints.method(message_types.VoidMessage, HangoutForms, 
            path='votedWaiting', 
            http_method='GET', name='votedWaiting')
    def votedWaiting(self, request):
        print "here bitch!!!"
        #Query the database Hangout.get()
        #put that into the form for showcasing everything, create the model
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)
        p_key = ndb.Key(Profile, user_id)
        userData=p_key.get()
        
        
        #handle the string processing
        eventsWaitingOn = json.loads(userData.eventsWaitingOn)
        eventList=[]
        form = HangoutForm()
        for eventId in eventsWaitingOn:
            #get the event from ndb
            event = ndb.Key(Hangout, eventId).get()

            eventList.append(event) 

        #return request
        return HangoutForms(items=[self._copyHangoutToForm(hangout) for hangout in eventList])

    @endpoints.method(message_types.VoidMessage, message_types.VoidMessage, 
        path='done', 
        http_method='GET', name='done')
    def done(self, request):
        #How do you know you event voting is done?
        #check your done queue. Should have been handled during event creation

        return request

api = endpoints.api_server([ConferenceApi]) # register API

#Sample Code to help me out. Reminder Code
    #data = Hangout.query()
    #for p in data:
    #    print p.key.id()
    #    print p.key.urlsafe()

    #to get a key query the objects then:
    #queryObj.key for ndb
    #queryObj.key() was the old db

    #Profile.Query(current user)
    #You need the key object then do a urlsafe()
    #then query more to get the list of objects 
    #p = Hangout.query().order(Hangout.date1)
    #    for x in p:
    #        print x.date1