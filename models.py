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

#Sign-in import Code will go here:
import re
import random
import hashlib
import hmac
from string import letters

import json

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

#DataBase Addition
def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

def users_key(group = 'default'):
    return ndb.Key('users', group)

class Profile(ndb.Model):
    """Profile -- User profile object"""
    displayName = ndb.StringProperty()
    firstName = ndb.StringProperty()
    lastName = ndb.StringProperty()
    mainEmail = ndb.StringProperty()
    #can be either a link, blobprop or blobkeyprop. not sure yet.
    profilePictureID = ndb.StringProperty()
    backupemail = ndb.StringProperty()
    pw_hash = ndb.StringProperty()
    cellphone = ndb.StringProperty()
    listOfContacts = ndb.JsonProperty()
    eventsInvited = ndb.JsonProperty()
    eventsWaitingOn = ndb.JsonProperty()
    eventsVoteDone = ndb.JsonProperty()
    eventsPassedDate = ndb.JsonProperty()
    eventsRegrets = ndb.JsonProperty()

    @classmethod
    def by_id(cls, uid):
        return Profile.get_by_id(uid)

    @classmethod
    def by_name(cls, name):
        u = Profile.query().filter(Profile.name == name).get()
        return u

    @classmethod
    def register(cls, firstName, lastName, password, email = None):
        pw_hash = make_pw_hash(email, password)
        return Profile(
                    key = ndb.Key(Profile, email),
                    firstName = firstName,
                    lastName = lastName,
                    pw_hash = pw_hash,
                    mainEmail = email,
                    eventsInvited = json.dumps([]),
                    eventsWaitingOn = json.dumps([]),
                    eventsVoteDone = json.dumps([]),
                    eventsPassedDate = json.dumps([]),
                    eventsRegrets = json.dumps([])
                    )
    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u

class ProfileMiniForm(messages.Message):
    """ProfileMiniForm -- update Profile form message"""
    displayName = messages.StringField(1)

class ProfileForm(messages.Message):
    """ProfileForm -- Profile outbound form message"""
    displayName = messages.StringField(1)
    mainEmail = messages.StringField(2)

class EmailRegFormInput(messages.Message):
    #This has to be unique - email (use as the id)
    email=messages.StringField(1)
    firstName=messages.StringField(2)
    lastName=messages.StringField(3)
    password=messages.StringField(4)

class Business(ndb.Model):
    businessName = ndb.StringProperty()
    locationName = ndb.StringProperty()
    mainEmail = ndb.StringProperty()
    password = ndb.StringProperty()
    phoneNumber = ndb.StringProperty()
    manager = ndb.StringProperty()
    employeesList = ndb.JsonProperty()
    #list of parties that are voting on your establishment
    votedOn = ndb.JsonProperty()
    #list of people in the area that are considering your specific place
    wantingToHang = ndb.JsonProperty()
    #parties that voted to hangout at your establishment
    firstPick = ndb.JsonProperty()
    #your discount deals
    discountDeals = ndb.JsonProperty()

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