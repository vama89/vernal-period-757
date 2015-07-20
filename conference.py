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
from models import VoteForm
from models import BooleanMessage

from settings import WEB_CLIENT_ID
from settings import ANDROID_CLIENT_ID
from settings import IOS_CLIENT_ID
from settings import ANDROID_AUDIENCE

from utils import getUserId

import json
import voting

EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID
MEMCACHE_ANNOUNCEMENTS_KEY = "RECENT_ANNOUNCEMENTS"
ANNOUNCEMENT_TPL = ('Last chance to attend! The following conferences '
                    'are nearly sold out: %s')
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

HANG_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    webSafeKey=messages.StringField(1),
)
#-------------------------

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
            elif field.name == "webSafeKey":
                setattr(hang, field.name, hangout.key.urlsafe())
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

        print request

        #Save information from html forms to Hangout Database.
        data = {field.name: getattr(request, field.name) for field in request.all_fields()}
        del data['webSafeKey']

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
        friendIDList=[]
        friendsDict={}
        friendsInJson=json.loads(data['friendList'])
        counter=1
        
        #I should really pass the friendID not just the name. Be sure to switch this
        #later in production
        for friend in friendsInJson:
            if friend == None:
                pass
            elif friend == "":
                pass
            else:
                #I have to get check the user's profileID here and do a database query of somesort.
                #i'll have the user's name - this is the whole search feature
                #based off the user name....how will I get the right userID/right person...the creator has to pick it for me

                #Search within the database to find the user. At this time, I must search their userID
                #I'll have to setup extra structures in order to search by name
                #1.)search by name
                #2.)Search by incorrect spelling
                #3.)Search by email and phone number

                #grab the key
                #friend_key = ndb.Key(Profile, friend)

                #then place the key within the list of friend keys to carry out processes below
                #friendKeyList.append(friend_key)
                friendIDList.append(friend)

                p ={"profileID" : friend, "voteRank" : [0,0,0], "firstChoie" : 0, "confirmation" :0}
                friendsDict[friend] = p
                counter=counter+1

                #then I have to get the friend's id (like I do with my own username
                #thenquery their profile
                #then just add them to the list of id's as I need to finish creating this event first
                #friendID list*******
                #proceed to after saving to the hangout below

        #Handle in this area, those that are not found within our system
        data['friendList'] = json.dumps(friendsDict)

        ###Add Event Creator 
        data['eventCreator'] = str(user_id)

        #process the user's own voting preferences
        data['groupVoteRanks'] = json.dumps([data['groupVoteRanks']])

        ####Add the Total Party Count
        data['totalCounter'] = 1
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
        
        for friendID in friendIDList:
            friendObject = ndb.Key(Profile, friendID).get()
            if friendObject.eventsInvited == None:
                eventsInvited = []
                for event in hangoutQry:
                    eventKey = event.key.id()
                    eventsInvited.append(eventKey)
                    friendObject.eventsInvited = json.dumps(eventsInvited)
                    friendObject.put()
            else:
                eventsInvited=json.loads(friendObject.eventsInvited)
                for event in hangoutQry:
                    eventKey = event.key.id()
                    eventsInvited.append(eventKey)
                    friendObject.eventsInvited = json.dumps(eventsInvited)
                    friendObject.put()

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

        return HangoutForms(items=[self._copyHangoutToForm(hangout) for hangout in eventList])

    @endpoints.method(message_types.VoidMessage, HangoutForms, 
            path='votedWaiting', 
            http_method='GET', name='votedWaiting')
    def votedWaiting(self, request):
        print "votedWaiting"
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

    @endpoints.method(message_types.VoidMessage, HangoutForms, 
        path='done', 
        http_method='GET', name='done')
    def done(self, request):
        #How do you know you event voting is done?
        #check your done queue. Should have been handled during event creation
        print "Done"
        
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)
        p_key = ndb.Key(Profile, user_id)
        userData=p_key.get()

        #handle the string processing
        eventsVoteDone = json.loads(userData.eventsVoteDone)
        eventList=[]
        form = HangoutForm()
        for eventId in eventsVoteDone:
            #get the event from ndb
            event = ndb.Key(Hangout, eventId).get()

            eventList.append(event)

        return HangoutForms(items=[self._copyHangoutToForm(hangout) for hangout in eventList])

    @endpoints.method(VoteForm, VoteForm, 
        path='vote', 
        http_method='POST', name='vote')
    def vote(self, request):
        #How do you know you event voting is done?
        #check your done queue. Should have been handled during event creation
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)
        p_key = ndb.Key(Profile, user_id)
        userObject = p_key.get()

        data = {field.name: getattr(request, field.name) for field in request.all_fields()}

        #get the proper hangout object
        hangoutObject = ndb.Key(urlsafe=data['webSafeKey']).get()

        #input the votes recieved from the form
        userVotes=[]
        userVotes.append(int(data['option1']))
        userVotes.append(int(data['option2']))
        userVotes.append(int(data['option3']))

        #add the last users' vote to the friend list, in his or her name
        friendList = json.loads(hangoutObject.friendList)
        friendList[user_id]['voteRank'] = userVotes

        #add the last user's vote to the hangout object groupVoteRanks
        groupVoteRanks = json.loads(hangoutObject.groupVoteRanks)
        for uni in groupVoteRanks:
            if type(uni) == unicode:
                listType=[]
                for p in uni:
                    for t in p:
                        if t == '[':
                            pass    
                        elif t == ',':
                            pass
                        elif t == ']':
                            pass
                        #elif t == '':
                        #    print t
                        elif t == ' ':
                            pass
                        else:
                            listType.append(int(t))
                groupVoteRanks.remove(uni)
                groupVoteRanks.append(listType)

        groupVoteRanks.append(userVotes)
        
        #if the totalcounter is 1 less than the partyTotal
        if hangoutObject.totalCounter == (hangoutObject.partyTotal - 1):
        #pull up people's profiles in the friend's list
        #delete hangout key from the waiting list
        #add it to the events done list
            friendList=json.loads(hangoutObject.friendList)
            friendListKeys=friendList.keys()
            for friendKey in friendListKeys:
                friendObject = ndb.Key(Profile, friendKey).get()
                eventsInvited = json.loads(friendObject.eventsInvited)
                for eventKey in eventsInvited:
                    if eventKey == hangoutObject.key.id():
                        eventsInvited.remove(eventKey)
                        friendObject.eventsInvited = json.dumps(eventsInvited)
                        if friendObject.eventsVoteDone == None:
                            eventsVoteDone = friendObject.eventsVoteDone
                            eventsVoteDone = []
                            eventsVoteDone.append(eventKey)
                            friendObject.eventsVoteDone = json.dumps(eventsVoteDone)
                            friendObject.put()
                        else:
                            eventsVoteDone = json.loads(friendObject.eventsVoteDone)
                            eventsVoteDone.append(eventKey)
                            friendObject.eventsVoteDone = json.dumps(eventsVoteDone)
                            friendObject.put()
                    else:
                        pass

        #remove the creator from him waiting
        #delete hangout key from the waiting list
        #add it to the events done list
            eventCreator = ndb.Key(Profile, hangoutObject.eventCreator).get()
            eventsWaitingOn = json.loads(eventCreator.eventsWaitingOn)
            for eventKey in eventsWaitingOn:
                if eventKey == hangoutObject.key.id():
                    eventsWaitingOn.remove(eventKey)
                    eventCreator.eventsWaitingOn = json.dumps(eventsWaitingOn)
                    if eventCreator.eventsVoteDone == None:
                        eventsVoteDone = eventCreator.eventsVoteDone
                        eventsVoteDone = []
                        eventsVoteDone.append(eventKey)
                        eventCreator.eventsVoteDone = json.dumps(eventsVoteDone)
                        eventCreator.put()
                    else:
                        eventsVoteDone = json.loads(eventCreator.eventsVoteDone)
                        eventsVoteDone.append(eventKey)
                        eventCreator.eventsVoteDone = json.dumps(eventsVoteDone)
                        eventCreator.put()
                else:
                    pass

        #tally-up the votes
            #run the voting algorithm and get the result
            results = voting.inViteVote(groupVoteRanks)
            #the results will come in a list the option that gets the least amount of votes is first pick, then second and so on
            hangoutObject.finalResults = json.dumps(results)

            #update the counter
            hangoutObject.totalCounter = hangoutObject.totalCounter + 1
            hangoutObject.votingCompleted = True

            hangoutObject.put()
            

        #if you still need to wait for peopel to vote
        else:
            #if voting will not completed then
            #updated the vote area for the algorithm of voting
            groupVoteRanks = json.loads(hangoutObject.groupVoteRanks)
            for uni in groupVoteRanks:
                if type(uni) == unicode:
                    listType=[]
                    for p in uni:
                        for t in p:
                            if t == '[':
                                pass    
                            elif t == ',':
                                pass
                            elif t == ']':
                                pass
                            #elif t == '':
                            #    print t
                            elif t == ' ':
                                pass
                            else:
                                listType.append(int(t))
                    groupVoteRanks.remove(uni)
                    groupVoteRanks.append(listType)

            groupVoteRanks.append(userVotes)
            hangoutObject.groupVoteRanks = json.dumps(groupVoteRanks)

            #update the user's voting preference
            friendList = json.loads(hangoutObject.friendList)
            friendList[user_id]['voteRank'] = userVotes

            #move this hangout to the voted waiting for this user
            eventsInvited = json.loads(userObject.eventsInvited)
            for eventKey in eventsInvited:
                if eventKey == hangoutObject.key.id():
                    #remove from the invited queue
                    eventsInvited.remove(eventKey)
                    userObject.eventsInvited = json.dumps(eventsInvited)

                    #place in the waiting queue
                    if userObject.eventsWaitingOn == None:
                        eventsWaitingOn = []
                        eventsWaitingOn.append(eventKey)
                        userObject.eventsWaitingOn = json.dumps(eventsWaitingOn)
                        userObject.put()
                    else:
                        eventsWaitingOn = json.loads(userObject.eventsWaitingOn)
                        eventsWaitingOn.append(eventKey)
                        userObject.eventsWaitingOn = json.dumps(eventsWaitingOn)
                        userObject.put()
                else:
                    pass

            #update the counter
            hangoutObject.totalCounter = hangoutObject.totalCounter + 1

            hangoutObject.put()

        return request

    @endpoints.method(HANG_GET_REQUEST, HangoutForms, 
        path='getResults/{webSafeKey}', 
        http_method='GET', name='getResults')
    def getResults(self, request):        
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)
        p_key = ndb.Key(Profile, user_id)
        userData=p_key.get()

        #get event and place it in list to copy to the form
        hangoutObject = ndb.Key(urlsafe=request.webSafeKey).get()
        eventList=[]
        eventList.append(hangoutObject)

        #t = message_types.VoidMessage()
        #return t
        return HangoutForms(items=[self._copyHangoutToForm(hangout) for hangout in eventList])

    @endpoints.method(HANG_GET_REQUEST, BooleanMessage, 
        path='stillVoting/{webSafeKey}', 
        http_method='GET', name='stillVoting')
    def stillVoting(self, request):        
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)
        p_key = ndb.Key(Profile, user_id)
        userData=p_key.get()

        #get event and place it in list to copy to the form
        hangoutObject = ndb.Key(urlsafe=request.webSafeKey).get()
        truthValue = hangoutObject.votingCompleted

        #t = message_types.VoidMessage()
        #return t
        return BooleanMessage(data=truthValue) 

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