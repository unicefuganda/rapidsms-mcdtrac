from django import template
from rapidsms.models import Connection

def hc(obj):
    try:
        contact = Connection.objects.filter(identity=obj)[0].contact
        if contact:
            hp = contact.healthproviderbase
            if hp:
                if hp.facility:
                    return '%s %s' % (hp.facility.name, hp.facility.type.name)
                else:
                    return ''
    except AttributeError:
        return ''
    
def district(obj):
    try:
        contact = Connection.objects.filter(identity=obj)[0].contact
        if contact:
            return contact.reporting_location
#            hp = contact.healthproviderbase
#            if hp:
#                if hp.facility:
#                    return '%s %s' % (hp.facility.name, hp.facility.type.name)
#                else:
#                    return ''
    except AttributeError:
        return ''

register = template.Library()

register.filter('hc', hc)
register.filter('district', district)
