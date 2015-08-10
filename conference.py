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
from models import VoteForm
from models import ProfileForms
from models import EmailRegForm
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
                mainEmail= user.email(),
                eventsInvited=[],
                eventsWaitingOn=[],
                eventsVoteDone=[],
                eventsPassedDate=[],
                eventsRegrets=[],
                confirmation =True
            )
            profile.put()

        return profile      # return Profile


    def _doProfile(self, save_request=None):
        """Get user Profile and return to user, possibly updating it first."""
        # get user Profile
        prof = self._getProfileFromUser()
        if prof.confirmation == False:
            prof.confirmation = True

            eventsInvited = prof.eventsInvited
            for hangoutId in eventsInvited:
                hangoutObject = ndb.Key(Hangout, hangoutId).get()
                #then for each hangout that is in your invited queue, place yourself in the friendlist 
                p = {"profileID" : prof.mainEmail, "voteRank" : [0,0,0], "firstChoie" : 0, "confirmation" :0}
                friendList = json.loads(hangoutObject.friendList)
                friendList[prof.mainEmail] = p
                hangoutObject.friendList = json.dumps(friendList)

                #removed yourself from the notInSystem list
                notInSystem = json.loads(hangoutObject.notInSystem)
                notInSystem.remove(prof.mainEmail)
                hangoutObject.notInSystem = json.dumps(notInSystem)

                hangoutObject.put()

            prof.put()

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

    def _doNotInSystemRegs(self, request):
        p_key= ndb.Key(Profile, request)

        profile = Profile(
            key = p_key,
            displayName = request,
            mainEmail= request,
            eventsInvited=[],
            eventsWaitingOn=[],
            eventsVoteDone=[],
            eventsPassedDate=[],
            eventsRegrets=[],
            confirmation=False
        )
        profile.put()

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

    @endpoints.method(EmailRegForm, message_types.VoidMessage,
            path='emailRegs', http_method='POST', name='emailRegs')
    def emailRegs(self, request):
        """Update & return user profile."""
        data = {field.name: getattr(request, field.name) for field in request.all_fields()}
        
        #find if the email is already a profile in the system
        profileObj = ndb.Key(Profile, data['email']).get()
        if profileObj:
            pass
            #return something indicating entry was a failure. Write something on the client
        else:
            #create the profile with the information
            p_key = ndb.Key(Profile, data['email'])

            profile = Profile(
                key = p_key,
                displayName = data['email'],
                mainEmail= data['email'],
                password = data['password'],
                firstName= data['firstName'],
                lastName= data['lastName'],
                eventsInvited=[],
                eventsWaitingOn=[],
                eventsVoteDone=[],
                eventsPassedDate=[],
                eventsRegrets=[],
                confirmation =True
            )
            profile.put()

        return message_types.VoidMessage()

    @endpoints.method(message_types.VoidMessage, BooleanMessage,
            path='isRegistered', http_method='GET', name='isRegistered')
    def isRegistered(self, request):
        """Return user profile."""
        #getUserInformationHere
        return BooleanMessage(data=True)

# - - - Hangout - - - - - - - - - - - - - - - - - - - - - - - 
    def _copyHangoutToForm(self, hangout):
        hang = HangoutForm()
        for field in hang.all_fields():
            if hasattr(hangout, field.name):
                if field.name in ('date1', 'date2', 'date3', 'time1', 'time2', 'time3', 'deadlineDate',\
                 'deadlineTime', 'dateEventCreated', 'totalCounter', 'partyTotal', 'votingCompleted', 'finalResults'):
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
        #getUserInformationHere
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)
        p_key = ndb.Key(Profile, user_id)

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
        friendIDList=[]
        friendsDict={}
        friendsInJson=json.loads(data['friendList'])
        friendsInJson.append(user_id)
        counter=0
        
        #Passing in emails
        #for this version, the friend is an email ID
        for friend in friendsInJson:
            if friend == None:
                pass
            elif friend == "":
                pass
            else:
                friendIDList.append(friend)

                p ={"profileID" : friend, "voteRank" : [0,0,0], "firstChoie" : 0, "confirmation" :0}
                friendsDict[friend] = p
                counter=counter+1

        data['friendList'] = json.dumps(friendsDict)

        ###Add Event Creator 
        data['eventCreator'] = str(user_id) 

        #User's Voting Preferences. Translating unicode to an integer of strings.
        listType=[]
        for uni in data['groupVoteRanks']:
            if type(uni) == unicode:
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
        #must be a list of the list NOTICE BRACKETS!!!!!!
        data['groupVoteRanks'] = json.dumps([listType])

        #just the list
        #initialize with users first votes
        adjustList=[]
        for p in listType:
            adjustNum=4-p
            adjustList.append(adjustNum)
        #THIS IS THE BARGRAHP ADJUSTED VOTE RANKS
        data['finalResults'] = json.dumps(adjustList)

        #adding the creator's vote preferences to the friendList REGULAR VOTERANK
        friendList = json.loads(data['friendList'])
        friendList[user_id]['voteRank'] = listType
        data['friendList'] = json.dumps(friendList)

        ####Add the Total Party Count
        data['totalCounter'] = 1
        ####Add the Party Total
        data['partyTotal'] = counter

        ###Voting Completed
        data['votingCompleted'] = False

        #place into the database
        Hangout(**data).put()
        #wait for it to generate the keys
        time.sleep(.1)

        #Query the hangout. This must be unique. Note to self. Find if there is a way to get the key before it is created.
        hangoutQry = Hangout.query(Hangout.eventCreator == str(user_id), Hangout.dateEventCreated == data['dateEventCreated'])
        #Getting the key
        hangoutKey=None
        for event in hangoutQry:
            hangoutKey = event.key.id()

        #Placing event key  in Creator's Waiting Queue
        creatorObj = p_key.get()
        
        eventsWaitingOn=creatorObj.eventsWaitingOn

        for event in hangoutQry:
            eventKeyId = event.key.id()
            eventsWaitingOn.append(eventKeyId)
            creatorObj.eventsWaitingOn = eventsWaitingOn
        creatorObj.put()

        #Placing event key to all friends except the creator.        
        for friendID in friendIDList:
            friendObject = ndb.Key(Profile, friendID).get()
            if friendObject:
                if friendObject == creatorObj:
                    pass
                else:
                    eventsInvited=friendObject.eventsInvited
                    for event in hangoutQry:
                        eventKeyId = event.key.id()
                        eventsInvited.append(eventKeyId)
                        friendObject.eventsInvited = eventsInvited
                        friendObject.put()
            else:
                pass

        #handle those that were not found...Register them
        notInSystem = json.loads(data['notInSystem'])
        for friend in notInSystem:
            #check to see they really are not in the system
            #that they didn't miss them in the friend add.
            prof = ndb.Key(Profile, friend).get()
            if prof:
                #do not create a profile again, it'll just add them in the key below
                print "test success"
            else:
                #add them into the system
                self._doNotInSystemRegs(friend)
        
        #place the hangout key in each one of the new regesterees
        for friend in notInSystem:
            obj = ndb.Key(Profile, friend).get()
            eventsInvited = obj.eventsInvited
            eventsInvited.append(hangoutKey)
            obj.eventsInvited = eventsInvited
            obj.put()
        
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
        eventsInvited = userData.eventsInvited
        eventList=[]
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
        eventsWaitingOn = userData.eventsWaitingOn
        eventList=[]
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
        eventsVoteDone = userData.eventsVoteDone
        eventList=[]
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

        #account for people that cannot attend at all. just null out their votes
        #check the creator

        #add the users vote to the friend list, in his or her name
        friendList = json.loads(hangoutObject.friendList)
        friendList[user_id]['voteRank'] = userVotes
        hangoutObject.friendList = json.dumps(friendList)

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

        #should have placed the user who voted in this collection of all the other users' votes
        groupVoteRanks.append(userVotes)
        hangoutObject.groupVoteRanks = json.dumps(groupVoteRanks)
        
        #if the totalcounter is 1 less than the partyTotal
        if hangoutObject.totalCounter == (hangoutObject.partyTotal - 1):
        #pull up people's profiles in the friend's list
        #delete hangout key from the waiting list
        #add it to the events done list
            friendList=json.loads(hangoutObject.friendList)
            friendListKeys=friendList.keys()
            for friendKey in friendListKeys:
                friendObject = ndb.Key(Profile, friendKey).get()
                eventsInvited = friendObject.eventsInvited
                for eventKey in eventsInvited:
                    if eventKey == hangoutObject.key.id():
                        eventsInvited.remove(eventKey)
                        friendObject.eventsInvited = eventsInvited

                        eventsVoteDone = friendObject.eventsVoteDone
                        eventsVoteDone.append(eventKey)
                        friendObject.eventsVoteDone = eventsVoteDone
                        friendObject.put()
                    else:
                        pass

        #remove the creator from him waiting
        #delete hangout key from the waiting list
        #add it to the events done list
            eventCreator = ndb.Key(Profile, hangoutObject.eventCreator).get()
            eventsWaitingOn = eventCreator.eventsWaitingOn
            for eventKey in eventsWaitingOn:
                if eventKey == hangoutObject.key.id():
                    eventsWaitingOn.remove(eventKey)
                    eventCreator.eventsWaitingOn = eventsWaitingOn

                    eventsVoteDone = eventCreator.eventsVoteDone
                    eventsVoteDone.append(eventKey)
                    eventCreator.eventsVoteDone = eventsVoteDone
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

            #Here add people's confirmation of whether they can go or not or maybe
            #based off of the winner check if people's preferences match the result.
            #if not then adjust their confirmation number accordinginly then parse it in javascript.

            maxOfResults = max(results)
            optionNumber = results.index(maxOfResults)

            friendList = json.loads(hangoutObject.friendList)
            #check people's first preference
            friends = friendList.keys()
            for friend in friends:
                voteRank = friendList[friend]['voteRank']
                minOf = min(friendList[friend]['voteRank'])
                firstChoice = voteRank.index(minOf)

                if firstChoice == optionNumber:
                    friendList[friend]['confirmation'] = 1
                else:
                    pass

            hangoutObject.friendList = json.dumps(friendList)

            hangoutObject.put()
            

        #if you still need to wait for peopel to vote
        else:
            #tally-upvotes
            #run the voting algorithm and get the result
            results = voting.inViteVote(groupVoteRanks)
            #the results will come in a list the option that gets the least amount of votes is first pick, then second and so on
            hangoutObject.finalResults = json.dumps(results)

            #update the user's voting preference
            #friendList = json.loads(hangoutObject.friendList)
            #friendList[user_id]['voteRank'] = userVotes
            #hangoutObject.friendList = json.dumps(friendList)

            #move this hangout to the voted waiting for this user
            eventsInvited = userObject.eventsInvited
            for eventKey in eventsInvited:
                if eventKey == hangoutObject.key.id():
                    #remove from the invited queue
                    eventsInvited.remove(eventKey)
                    userObject.eventsInvited = eventsInvited

                    #place in the waiting queue
                    eventsWaitingOn = userObject.eventsWaitingOn
                    eventsWaitingOn.append(eventKey)
                    userObject.eventsWaitingOn = eventsWaitingOn
                    userObject.put()
                else:
                    pass

            #update the counter
            hangoutObject.totalCounter = hangoutObject.totalCounter + 1

            hangoutObject.put()

        return request

    @endpoints.method(HANG_GET_REQUEST, HangoutForms, 
        path='getResultsWaiting/{webSafeKey}', 
        http_method='GET', name='getResultsWaiting')
    def getResultsWaiting(self, request):        
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

    @endpoints.method(HANG_GET_REQUEST, HangoutForms, 
        path='getResultsFinal/{webSafeKey}', 
        http_method='GET', name='getResultsFinal')
    def getResultsFinal(self, request):        
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
    
    @endpoints.method(message_types.VoidMessage, ProfileForms, 
        path='test', 
        http_method='GET', name='test')
    def test(self, request):        
        #get all the people in the database and return an object in FriendSearchForm format
        profiles = Profile.query()

        return ProfileForms(items=[self._copyProfileToForm(profile) for profile in profiles])
        #return request

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