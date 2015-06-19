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

class Profile(ndb.Model):
    """Profile -- User profile object"""
    displayName = ndb.StringProperty()
    mainEmail = ndb.StringProperty()
    #can be either a link, blobprop or blobkeyprop. not sure yet.
    profilePictureID = ndb.StringProperty()
    backupemail = ndb.StringProperty()
    password = ndb.StringProperty()
    cellphone = ndb.StringProperty()
    listOfContacts = ndb.StringProperty()
    eventsInvited = ndb.StringProperty()
    eventsWaitingOn = ndb.StringProperty()
    eventsVoteDone = ndb.StringProperty()
    eventsPassedDate = ndb.StringProperty()
    eventsRegrets = ndb.StringProperty()

class ProfileMiniForm(messages.Message):
    """ProfileMiniForm -- update Profile form message"""
    displayName = messages.StringField(1)

class ProfileForm(messages.Message):
    """ProfileForm -- Profile outbound form message"""
    displayName = messages.StringField(1)
    mainEmail = messages.StringField(2)

class Business(ndb.Model):
    businessName = ndb.StringProperty()
    locationname = ndb.StringProperty()
    mainEmail = ndb.StringProperty()
    password = ndb.StringProperty()
    phoneNumber = ndb.StringProperty()
    manager = ndb.StringProperty()
    employeesList = ndb.StringProperty()
    #list of parties that are voting on your establishment
    votedOn = ndb.StringProperty()
    #list of people in the area that are considering your specific place
    wantingtoHang = ndb.StringProperty()
    #parties that voted to hangout at your establishment
    firstPick = ndb.StringProperty()
    #your discount deals
    discountDeals = ndb.StringProperty()

#My Additions The Hangout Code
class Hangout(ndb.Model):
    eventName = ndb.StringProperty()
    description = ndb.StringProperty()
    date1 = ndb.StringProperty()
    date2 = ndb.StringProperty()
    date3 = ndb.StringProperty()
    locationname1 = ndb.StringProperty()
    locationname2 = ndb.StringProperty()
    locationname3 = ndb.StringProperty()
    place1 = ndb.StringProperty()
    place2 = ndb.StringProperty()
    place3 = ndb.StringProperty()
    time1 = ndb.StringProperty()
    time2 = ndb.StringProperty()
    time3 = ndb.StringProperty()
    #administrative items
    eventCreator=ndb.StringProperty()
    friendList=ndb.StringProperty()
    #do a dictionary of the vote ranks based of the friendList
    voteRanks=ndb.StringProperty()
    deadlineDate=ndb.StringProperty()
    dateEventCreated=ndb.StringProperty()

class HangoutForm(messages.Message):
    eventName = messages.StringField(1)
    description = messages.StringField(2)
    date1 = messages.StringField(3)
    date2 = messages.StringField(4)
    date3 = messages.StringField(5)
    locationname1 = messages.StringField(6)
    locationname2 = messages.StringField(7)
    locationname3 = messages.StringField(8)
    place1 = messages.StringField(9)
    place2 = messages.StringField(10)
    place3 = messages.StringField(11)
    time1 = messages.StringField(12)
    time2 = messages.StringField(13)
    time3 = messages.StringField(14)
    #administrative items
    eventCreator=messages.StringField(15)
    friendList=messages.StringField(16)
    voteRanks=messages.StringField(17)
    deadlineDate=messages.StringField(18)
    dateEventCreated=messages.StringField(19)