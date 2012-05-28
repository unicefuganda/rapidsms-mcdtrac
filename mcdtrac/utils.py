'''
Created on May 28, 2012

@author: asseym
'''
from healthmodels.models.HealthProvider import HealthProvider
from healthmodels.models.HealthFacility import HealthFacility
from rapidsms.contrib.locations.models import Location
from rapidsms.models import Contact
from django.db.models import Count
from uganda_common.utils import *
from rapidsms_httprouter.models import Message

def last_reporting_period(period=1, weekday=getattr(settings, 'FIRSTDAY_OF_REPORTING_WEEK', 3), todate=False):
    """
    Find a date range that spans from the most recent Wednesday (exactly a week ago if
    today is Wednesday) to the beginning of Thursday, one week prior
    
    if period is specified, this wednesday can be exactly <period> weeks prior
    """
    d = datetime.datetime.now()
    d = datetime.datetime(d.year, d.month, d.day)
    # find the past day with weekday() of 3
    last_thursday = d - datetime.timedelta((((7 - weekday) + d.weekday()) % 7)) - datetime.timedelta((period - 1) * 7)
    return (last_thursday - datetime.timedelta(7), datetime.datetime.now() if todate else last_thursday,)

def total_facilities(location, count=True):
    """
    Find all health facilities whose catchment areas are somewhere inside
    the passed in location.
    
    Return their count if count is True, otherwise return the queryset
    """
    if not location:
        location = Location.tree.root_nodes()[0]
    locations = location.get_descendants(include_self=True).all()
    facilities = HealthFacility.objects.filter(catchment_areas__in=locations).distinct()
    if count:
        return facilities.count()

    return facilities

def get_area(request):
    if request.user.is_authenticated() and Location.objects.filter(type__name='district', name=request.user.username).count():
        area = Location.objects.filter(type__name='district', name=request.user.username)[0]
    elif request.user.is_authenticated() and Contact.objects.filter(user=request.user).count():
        area = Contact.objects.filter(user=request.user)[0].reporting_location
    else:
#        area = Location.tree.root_nodes()[0]
#        area = Location.objects.get(name='Uganda')
        area = Location.tree.filter(level__lt=1)[0]
    return area

def get_reporters(**kwargs):
    request = kwargs.pop('request')
    area = get_area(request)
    toret = HealthProvider.objects.filter(active=True)
    print toret
    if area:
        toret = toret.filter(reporting_location__in=area.get_descendants(include_self=True).all()).select_related('facility', 'location').annotate(Count('connection__submissions')).all()
    return toret.select_related('facility', 'location').annotate(Count('connection__submissions')).all()

def get_unsolicited_messages(**kwargs):
    request = kwargs.pop('request')

    # get all unsolicited messages
    messages = get_messages(request)

    # now filter by user's location
    location = get_location_for_user(request.user)
    messages = messages.filter(connection__contact__reporting_location__in=location.get_descendants(include_self=True).all())
    # get rid of unregistered, anonymous, and trainee connections
    messages = messages.exclude(connection__contact=None).exclude(connection__contact__active=False)
    messages = messages.order_by('-date')
    return messages

def get_all_messages(**kwargs):
    """
    Get all messages that are direct responses to polls (not related to the anonymous hotline)
    """
    request = kwargs.pop('request')
    area = get_location_for_user(request)
    if not area == Location.tree.root_nodes()[0]:
        return Message.objects.exclude(connection__identity__in=getattr(settings, 'MODEM_NUMBERS', ['256777773260', '256752145316', '256711957281', '256790403038', '256701205129'])).\
            exclude(connection__backend__name="yo8200").filter(direction='I', connection__contact__reporting_location__in=area.get_descendants(include_self=True).all()).order_by('-date')

    return Message.objects.exclude(connection__identity__in=getattr(settings, 'MODEM_NUMBERS', ['256777773260', '256752145316', '256711957281', '256790403038', '256701205129'])).\
        exclude(connection__backend__name="yo8200").filter(direction='I').order_by('-date')

#def get_mass_messages(**kwargs):
#    request = kwargs.pop('request')
#    if request.user.is_authenticated():
#        return [(p.question, p.start_date, p.user.username, p.contacts.count(), 'Poll Message') for p in Poll.objects.filter(user=request.user).exclude(start_date=None)] + [(m.text, m.date, m.user.username, m.contacts.count(), 'Mass Text') for m in MassText.objects.filter(user=request.user)]
#    return [(p.question, p.start_date, p.user.username, p.contacts.count(), 'Poll Message') for p in Poll.objects.exclude(start_date=None)] + [(m.text, m.date, m.user.username, m.contacts.count(), 'Mass Text') for m in MassText.objects.all()]

def get_district_for_facility(hc):
    bounds = hc.catchment_areas.aggregate(Min('lft'), Max('rght'))
    l = Location.objects.filter(lft__lte=bounds['lft__min'], rght__gte=bounds['rght__max'], type__name='district')
    if l.count():
        return l[0]
    return None

def get_staff_for_facility(facilities):
    hc_role = Group.objects.get(name='HC')
    return HealthProvider.objects.filter(groups=hc_role, facility__in=facilities)

def get_latest_report(facility, keyword=None):
    facilities = HealthFacility.objects.filter(pk=facility.pk)
    staff = get_staff_for_facility(facilities)
    try:
        if keyword:
            return XFormSubmission.objects.filter(xform__keyword=keyword, message__connection__contact__in=staff)\
                .latest('created')
        else:
            return XFormSubmission.objects.filter(message__connection__contact__in=staff)\
                .latest('created')
    except XFormSubmission.DoesNotExist:
        return None
    
def get_last_reporting_date(facility):
    report = get_latest_report(facility)
    if report:
        return report.created

    return None

def get_facility_reports(location, count=False, date_range=last_reporting_period(period=1, todate=True), approved=None):
    facilities = total_facilities(location, count=False)
    print date_range
    staff = get_staff_for_facility(facilities)
    toret = XFormSubmission.objects.filter(\
        connection__contact__in=staff, \
        has_errors=False).order_by('-created')
    if date_range:
        toret = toret.filter(created__range=date_range)
    if approved is not None:
        toret = toret.filter(approved=approved)

    if count:
        print toret.values('created', 'id')
        return toret.count()
    return toret

def reporting_facilities(location, facilities=None, count=True, date_range=None):
    facilities = facilities or total_facilities(location, count=False)
    staff = get_staff_for_facility(facilities)
    reporting = XFormSubmission.objects.filter(connection__contact__in=staff)
    if date_range:
        reporting = reporting.filter(created__range=date_range)

    reporting = reporting\
            .filter(has_errors=False)\
            .values('message__connection__contact__healthproviderbase__facility')\
            .annotate(Count('pk'))\
            .values('message__connection__contact__healthproviderbase__facility', \
                    'pk__count')

    if count:
        return reporting.count()

    return reporting
