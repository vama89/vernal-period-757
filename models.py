#!/usr/bin/env python

"""models.py

Udacity conference server-side Python App Engine data & ProtoRPC models

$Id: models.py,v 1.1 2014/05/24 22:01:10 wesc Exp $

created/forked from conferences.py by wesc on 2014 may 24

"""

__author__ = 'wesc+api@google.com (Wesley Chun)'

import httplib
import endpoints
from protorpc import messages
from google.appengine.ext import ndb

import json

class Profile(ndb.Model):
    """Profile -- User profile object"""
    displayName = ndb.StringProperty()
    mainEmail = ndb.StringProperty()
    listOfContacts = ndb.StringProperty(repeated=True)
    eventsInvited = ndb.IntegerProperty(repeated=True)
    eventsWaitingOn = ndb.IntegerProperty(repeated=True)
    eventsVoteDone = ndb.IntegerProperty(repeated=True)
    eventsPassedDate = ndb.IntegerProperty(repeated=True)
    eventsRegrets = ndb.IntegerProperty(repeated=True)

class ProfileMiniForm(messages.Message):
    """ProfileMiniForm -- update Profile form message"""
    displayName = messages.StringField(1)

class ProfileForm(messages.Message):
    """ProfileForm -- Profile outbound form message"""
    displayName = messages.StringField(1)
    mainEmail = messages.StringField(2)

class ProfileForms(messages.Message):
    items = messages.MessageField(ProfileForm, 1, repeated=True)

#My Additions The Hangout Code
class Hangout(ndb.Model):
    eventName = ndb.StringProperty()
    description = ndb.StringProperty()
    date1 = ndb.DateProperty()
    date2 = ndb.DateProperty()
    date3 = ndb.DateProperty()
    locationName1 = ndb.StringProperty()
    locationName2 = ndb.StringProperty()
    locationName3 = ndb.StringProperty()
    address1 = ndb.StringProperty()
    address2 = ndb.StringProperty()
    address3 = ndb.StringProperty()
    time1 = ndb.TimeProperty()
    time2 = ndb.TimeProperty()
    time3 = ndb.TimeProperty()
    #administrative items
    eventCreator=ndb.StringProperty()
    #populate the friendlist as a dictionary of name, key, and voteranks, confirmation if going to event if first choice was not picked.
    #friendlist is a list of friends[]. in the list each friend is structured as a dictionary
    friendList=ndb.JsonProperty()
    deadlineDate=ndb.DateProperty()
    deadlineTime=ndb.TimeProperty()
    dateEventCreated=ndb.DateTimeProperty()
    totalCounter=ndb.IntegerProperty()
    partyTotal=ndb.IntegerProperty()
    #voting ranks will take the for of dictionary. first, second, and expandable
    #if we are to increase user choices later on.
    #key to decipher final results is that the numbers inside refer to the options
    #then in the list[] index 0 is the first place choice
    finalResults=ndb.JsonProperty()
    votingCompleted=ndb.BooleanProperty()
    groupVoteRanks = ndb.JsonProperty()

class HangoutForm(messages.Message):
    eventName = messages.StringField(1)
    description = messages.StringField(2)
    date1 = messages.StringField(3)
    date2 = messages.StringField(4)
    date3 = messages.StringField(5)
    locationName1 = messages.StringField(6)
    locationName2 = messages.StringField(7)
    locationName3 = messages.StringField(8)
    address1 = messages.StringField(9)
    address2 = messages.StringField(10)
    address3 = messages.StringField(11)
    time1 = messages.StringField(12)
    time2 = messages.StringField(13)
    time3 = messages.StringField(14)
    #administrative items
    eventCreator=messages.StringField(15)
    #populate the friendlist as a dictionary of name, key, and voteranks, confirmation if going to event if first choice was not picked.
    friendList=messages.StringField(16)
    deadlineDate=messages.StringField(17)
    dateEventCreated=messages.StringField(18)
    totalCounter=messages.StringField(19)
    partyTotal=messages.StringField(20)
    #voting ranks will take the for of dictionary. first, second, and expandable
    #if we are to increase user choices later on.
    finalResults=messages.StringField(21)
    votingCompleted = messages.StringField(22)
    groupVoteRanks = messages.StringField(23)
    deadlineTime = messages.StringField(24)
    webSafeKey = messages.StringField(25)

class HangoutForms(messages.Message):
    items = messages.MessageField(HangoutForm, 1, repeated=True)

class VoteForm(messages.Message):
    option1 = messages.StringField(1)
    option2 = messages.StringField(2)
    option3 = messages.StringField(3)
    webSafeKey = messages.StringField(4)

class BooleanMessage(messages.Message):
    data = messages.BooleanField(1)

#class EventsWaitingForms(messages.Message):
#    items = messages.MessageField()