'''
Created on Jun 5, 2012

@author: asseym
'''
# -*- coding: utf-8 -*-
import rapidsms
import datetime

from rapidsms.apps.base import AppBase
from rapidsms_httprouter.models import Message,MessageBatch

class App(AppBase):

    def handle (self, message):
        print dir(message)
        if message.db_message.application != 'rapidsms_xforms':
            message.respond('We did not understand your message format, please reformat and send again!')
            return True
        return False