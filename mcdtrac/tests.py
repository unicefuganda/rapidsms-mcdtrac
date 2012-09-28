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
from logistics.models import ProductReport
from mtrack.loader import mtrack_init_demo


class MCDTests(TestCase): #pragma: no cover
#    fixtures = ["xform_reports.json", "pow_sum.json"]
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
        mtrack_init_demo()
        ProductReport.objects.all().delete()
        self.backend, c = Backend.objects.get_or_create(name='test')
        self.facility = HealthFacility.objects.all()[0]
        self.contact = Contact.objects.all()[0]
        hp = HealthProvider.objects.get(contact_ptr=self.contact)
        hp.facility = self.facility
        hp.save()
        self.connection = Connection.objects.get(contact=self.contact)

    def testReport(self):
        self.fake_incoming('dpt.2.3')
        week = 7 * 86400
        self.elapseTime(XFormSubmission.objects.all()[0], week * 2)
        self.assertEquals(Message.objects.all().order_by('-date')[0].text, 'You reported Male children 2, and Female children 3.If there is an error,please resend.')
    
    def testNonRegisteredReporter(self):
        self.fake_incoming('dpt.2.3', connection=Connection.objects.create(identity='12345', backend=self.backend))  
        self.assertEquals(Message.objects.all().order_by('-date')[0].text, 'You must be a reporter for FHDs. Please register first before sending any information')
          
    def testBadMessage(self):
        self.fake_incoming('bla bla')
        self.assertEquals(Message.objects.order_by('-date')[0].text, 'Thank you for your message. We have forwarded to your DHT for follow-up. If this was meant to be a weekly report, please check and resend.')
        
    def testLeftOutParameter(self):
        self.fake_incoming('dpt.2') 
        self.assertEquals(Message.objects.all().order_by('-date')[0].text, 'You reported Male children 2.If there is an error,please resend.')
        
    def testFHDMuac(self):
        self.fake_incoming('redm.2') 
        self.assertEquals(Message.objects.all().order_by('-date')[0].text, 'You reported Number of children 2.If there is an error,please resend.')
        
    def testFuzzyMatchNumber(self):
        self.fake_incoming('redm.I')
        self.assertEquals(Message.objects.all().order_by('-date')[0].text, 'You reported Number of children 1.If there is an error,please resend.')
        
        
        
        
        