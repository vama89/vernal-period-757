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

"""
class Profile(ndb.Model):
    displayName
    mainEmail
    backupemail
    password
    cellphone
    listOfContacts
    eventsInvited
    eventsWaitingOn
    eventVoteDone
    eventsPassed = {"eventID":123123, }

class Hangout(ndb.Model):
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
    eventCreator - Be sure to use a unique identifier
    friendList
    dateEventCreated
    dateEventVoteEnds

class Business(ndb.Model):
    businessName
    locationname
    manager
    employeesList

    listofPartiesConsideringVote
    listofPartieswantingToHangout
    Partiesthatpickedyourlocationtohangout
    discountDeals
        
"""
class Profile(ndb.Model):
    """Profile -- User profile object"""
    displayName = ndb.StringProperty()
    mainEmail = ndb.StringProperty()

class ProfileMiniForm(messages.Message):
    """ProfileMiniForm -- update Profile form message"""
    displayName = messages.StringField(1)

class ProfileForm(messages.Message):
    """ProfileForm -- Profile outbound form message"""
    displayName = messages.StringField(1)
    mainEmail = messages.StringField(2)

#My Additions The Hangout Code
class Hangout(ndb.Model):
    eventJsonInfo = ndb.TextProperty(required=True)

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