'''
Created on May 28, 2012

@author: asseym
'''
from healthmodels.models.HealthProvider import HealthProvider
from healthmodels.models.HealthFacility import HealthFacility
from rapidsms.contrib.locations.models import Location
from rapidsms.models import Contact
from django.db.models import Count, Max, Min
from uganda_common.utils import *
from rapidsms_httprouter.models import Message
from django.conf import settings
import os
import datetime
import dateutil
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

try:
    if not XFORMS:
        XFORMS = getattr(settings, 'MCDTRAC_XFORMS_KEYWORDS', ['dpt', 'vacm', 'vita', 'breg', 'pow', 'ryg', 'pcv', 'tetn', 'npet', 'ancp', 'heid', 'bpbs', 'dorm'])
except NameError:
    XFORMS = getattr(settings, 'MCDTRAC_XFORMS_KEYWORDS', ['dpt', 'vacm', 'vita', 'breg', 'pow', 'ryg', 'pcv', 'tetn', 'npet', 'ancp', 'heid', 'bpbs', 'dorm'])

try:
    if not OLD_XFORMS:
        OLD_XFORMS = getattr(settings, 'MCDTRAC_EXPIRED_KEYWORDS', ['worm', 'redm', 'tet', 'anc', 'eid', 'sum', 'summary'])
except NameError:
    OLD_XFORMS = getattr(settings, 'MCDTRAC_EXPIRED_KEYWORDS', ['worm', 'redm', 'tet', 'anc', 'eid', 'sum', 'summary'])

# ensure XFORMS doens't have what's in OLD_XFORMS
for x in OLD_XFORMS:
    try:
        XFORMS.remove(x)
    except:
        pass

XLS_DIR = getattr(settings, 'FHD_XLS_DIRECTORY', 'rapidsms_mcdtrac/mcdtrac/static/spreadsheets/')

def last_reporting_period(period=1, weekday=getattr(settings, 'FIRSTDAY_OF_REPORTING_WEEK', 3), todate=False, offset=None):
    """
    Find a date range that spans from the most recent Wednesday (exactly a week ago if
    today is Wednesday) to the beginning of Thursday, one week prior

    if period is specified, this wednesday can be exactly <period> weeks prior

    if offset is specified and is a datetime.datetime object, then calculate
    from offset rather than today.
    in which case the last date if todate=True is the offset.
    """
    if offset == None or not isinstance(offset, datetime.datetime):
        d = datetime.datetime.now()
    else:
        d = offset

    d = datetime.datetime(d.year, d.month, d.day)
    # find the past day with weekday() of 3
    last_thursday = d - datetime.timedelta((((7 - weekday) + d.weekday()) % 7)) - datetime.timedelta((period - 1) * 7)

    if todate:
        if not isinstance(offset, datetime.datetime):
            offset = datetime.datetime.now()
    else:
        offset = last_thursday

    return (last_thursday - datetime.timedelta(7), offset,)

def fhd_get_xform_dates(request):
    """
    Process date variables from POST
    """
    #    dates = {}
    dates = get_dates_from_post(request)
    if ('start' in dates) and ('end' in dates):
        request.session['start_date'] = dates['start']
        request.session['end_date'] = dates['end']
    elif request.GET.get('start_date', None) and request.GET.get('end_date', None):
        request.session['start_date'] = dates['start'] = \
        datetime.datetime.fromtimestamp(int(request.GET['start_date']))
        request.session['end_date'] = dates['end'] = end_date = \
        datetime.datetime.fromtimestamp(int(request.GET['end_date']))
    elif request.session.get('start_date', None) and request.session.get('end_date', None):
        dates['start'] = request.session['start_date']
        dates['end'] = request.session['end_date']
    dts = XFormSubmission.objects.filter(
                xform__keyword__in=XFORMS
            ).aggregate(
                Max('created'), Min('created')
            )
    dates['max'] = dts.get('created__max', None)
    dates['min'] = dts.get('created__min', None)
    dates.setdefault(
        'start',
        last_reporting_period(period=1, weekday=0, offset=dates['max'])[0]
    )
    dates.setdefault(
        'end',
        last_reporting_period(period=1, weekday=0, offset=dates['max'])[1] - datetime.timedelta(days=1)
    )
    return dates

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        OrderedDict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]
def generate_fpath(start_date=None, end_date=None, subdir='uganda', prefix='', suffix=''):
    """
    generate the path to the excel files.
    start_date and end_date must be date objects
    """
    custom_range = False

    if not start_date:
        quarter_months = ['01', '04', '07', '10']
        start_date = dateutil.parser.parse(
            str(datetime.date.today().year) + '-' +
            str(quarter_months[(datetime.date.today().month - 1) // 3]) + '-' +
            '01'
        ).date()
    else:
        custom_range = True

    if not end_date:
        end_date = datetime.date.today()
    else:
        custom_range= True

    q_str = 'Q' + str((start_date.month - 1) // 3 + 1)
    y_str = str(start_date.year)

    if custom_range:
        xls_fname = '{2}fhd_stats_{0}_{1}{3}.xlsx'.format(
            start_date.strftime('%F'),
            end_date.strftime('%F'),
            prefix.lower(),
            suffix.lower())
    else:
        xls_fname = '{2}fhd_stats-{0}_{1}{3}.xlsx'.format(
            y_str,
            q_str,
            prefix.lower(),
            suffix.lower())

    xls_fpath = os.path.join(
        settings.MTRACK_ROOT,
        XLS_DIR,
        '{0}/{1}'.format(subdir.lower(), y_str),
        xls_fname
    )
    return os.path.abspath(xls_fpath)

def generate_sql(sub_level=False, location_id=None):
    """
    generate SQL used to populate excel exports as follows:

    if sub_level = False:
        generate the strings suitable for a global level worksheets
    else:
        generate the sql suitable for a particular location specified
        as the <location_id> option. Raise Exception if no <location_id>
    """
    if sub_level:
        if not (location_id and isinstance(location_id, (int, long))):
            raise Exception("If you want a district give me a location_id")
        else:
            grp_sql_title = 'SELECT f.facility AS "Facility"'
            sql_id = 'l.id = {0}'.format(int(location_id))
            grp_sql_name = 'f.facility'
    else:
        grp_sql_title = 'SELECT l.name AS "District"'
        sql_id = """l.id in (SELECT "locations_location"."id"
            FROM "locations_location"
            WHERE ("locations_location"."lft" <= 15257
                   AND "locations_location"."lft" >= 2
                   AND "locations_location"."tree_id" = 1
                   AND "locations_location"."type_id" = E'district'))"""
        grp_sql_name = 'l.name'

    grouped_sql = """{0},
               COUNT(f.dpt_male) AS "Entries",
               SUM(dpt_male) AS "DPT (M)",
               SUM(dpt_female) AS "DPT (F)",
               SUM(vacm_male) AS "Measles (M)",
               SUM(vacm_female) AS "Measles (F)",
               SUM(vita_male1) AS "Vitamin A Males (6-11m)",
               SUM(vita_female1) AS "Vitamin A Females (6-11m)",
               SUM(vita_male2) AS "Vitamin A Males (12-59m)",
               SUM(vita_female2) AS "Vitamin A Females (12-59m)",
               SUM(worm_male) AS "Deworming (M)",
               SUM(worm_female) AS "Deworming (F)",
               SUM(redm_number) AS "MUAC in Red Zone",
               SUM(tet_dose2) AS "Tetanus dose2",
               SUM(tet_dose3) AS "Tetanus dose3",
               SUM(tet_dose4) AS "Tetanus dose4",
               SUM(tet_dose5) AS "Tetanus dose5",
               SUM(anc_number) AS "Four or more ANC visits",
               SUM(eid_male) AS "HIV Children < 1year (M)",
               SUM(eid_female) AS "HIV Children < 1year (F)",
               SUM(breg_male) AS "Birth Registration (M)",
               SUM(breg_female) AS "Birth Registration (F)",
               SUM(expected_pows) AS "Expected POWs",
               SUM(reached_pows) AS "Reached POWs"
        FROM fhd_stats_mview f,
             locations_location l
        WHERE f.has_errors = FALSE
            AND f.created >= %s
            AND f.created <= %s
            AND l.lft <= f.lft
            AND l.rght >= f.rght
            AND {1}
        GROUP BY l.lft,
                 l.id,
                 {2},
                 l.rght""".format(grp_sql_title, sql_id, grp_sql_name)

    individual_sql = """SELECT f.submission_id,
               f.created::date AS "Date",
               l.name AS district,
               f.facility AS facility,
            (SELECT ll.name
             FROM locations_location ll
             WHERE f.reporting_location_id = ll.id) AS "reporting location",
               f.reporting_name AS reporter,
               f.has_errors,
               f.dpt_male AS "DPT (M)",
               f.dpt_female AS "DPT (F)",
               f.vacm_male AS "Measles (M)",
               f.vacm_female AS "Measles (F)",
               f.vita_male1 AS "Vitamin A Males (6-11m)" ,
               f.vita_female1 AS "Vitamin A Females (6-11m)",
               f.vita_male2 AS "Vitamin A Males (12-59m)",
               f.vita_female2 AS "Vitamin A Females (12-59m)",
               f.worm_male AS "Deworming (M)",
               f.worm_female AS "Deworming (F)",
               f.redm_number AS "MUAC in Red Zone",
               f.tet_dose2 AS "Tetanus dose2",
               f.tet_dose3 AS "Tetanus dose3",
               f.tet_dose4 AS "Tetanus dose4",
               f.tet_dose5 AS "Tetanus dose5",
               f.anc_number AS "Four or more ANC visits",
               f.eid_male AS "HIV Children < 1year (M)",
               f.eid_female AS "HIV Children < 1year (F)",
               f.breg_male AS "Birth Registration (M)",
               f.breg_female AS "Birth Registration (F)",
               f.expected_pows AS "Expected POWs",
               f.reached_pows AS "Reached POWs"
        FROM fhd_stats_mview f ,
             locations_location l
        WHERE f.created >= %s
            AND f.created <= %s
            AND l.lft <= f.lft
            AND l.rght >= f.rght
            AND {0}""".format(sql_id)

    return (grouped_sql, individual_sql)


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
