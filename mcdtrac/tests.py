'''
Created on May 23, 2012

@author: asseym
'''
from django.test import TestCase
from django.conf import settings
import datetime
import traceback
from rapidsms_httprouter.router import get_router#, HttpRouterThread
from rapidsms_xforms.models import *
from rapidsms.messages.incoming import IncomingMessage, IncomingMessage
from rapidsms.models import Connection, Backend, Contact
from rapidsms_httprouter.models import Message
from rapidsms_httprouter.router import get_router
from django.contrib.auth.models import Group
from healthmodels.models import *
from django.db import connection
from rapidsms.contrib.locations.models import Location, LocationType


class ReportsTest(TestCase): #pragma: no cover

    def fake_incoming(self, message, connection=None):
        if connection is None:
            connection = self.connection
        router = get_router()
        return router.handle_incoming(connection.backend.name, connection.identity, message)


    def spoof_incoming_obj(self, message, connection=None):
        if connection is None:
            connection = Connection.objects.all()[0]
        incomingmessage = IncomingMessage(connection, message)
        incomingmessage.db_message = Message.objects.create(direction='I', connection=Connection.objects.all()[0], text=message)
        return incomingmessage

    def elapseTime(self, submission, seconds):
        newtime = submission.created - datetime.timedelta(seconds=seconds)
        cursor = connection.cursor()
        cursor.execute("update rapidsms_xforms_xformsubmission set created = '%s' where id = %d" %
                       (newtime.strftime('%Y-%m-%d %H:%M:%S.%f'), submission.pk))

    def setUp(self):
        if 'django.contrib.sites' in settings.INSTALLED_APPS:
            site_id = getattr(settings, 'SITE_ID', 6)
            Site.objects.get_or_create(pk=site_id, defaults={'domain':'mcdtrac.unicefuganda.org'})
        User.objects.get_or_create(username='admin')
        contact = Contact.objects.create(name='vht reporter')
        self.group = Group.objects.create(name='reporters')
        contact.groups.add(self.group)
        contact.active = True
        contact.save()
        hp = HealthProvider.objects.create(pk=contact.pk, name='vht reporter')
        self.point = Point.objects.create(latitude=10.0099288, longitude=21.0987398)
        self.district_type = LocationType.objects.create(name='district')
        self.mubende = Location.objects.create(name='Mubende', point=self.point, type=self.district_type)
        hf = HealthFacility.objects.create(name='HFacility', location=self.point)
        self.hp_group = hp.groups.add(self.group)
        hp.active = True
        hp.facility = hf
        hp.save()
        self.backend = Backend.objects.create(name='test')
        self.connection = Connection.objects.create(identity='8675309', backend=self.backend)
        self.connection.contact = contact
        self.connection.save()

    def testReport(self):
        self.fake_incoming('dpt3 2, 3')
        week = 7 * 86400
        self.elapseTime(XFormSubmission.objects.all()[0], week * 2)
        self.assertEquals(Message.objects.all().order_by('-date')[0].text, 'You reported Male 2, and Female 3.If there is an error,please resend.')
        self.assertEquals(XFormSubmission.objects.all()[0].connection.contact.healthproviderbase.healthprovider.facility.location, self.mubende)
        
        
        
        
        
        
        