from django import template
from django.shortcuts import get_object_or_404
from rapidsms.contrib.locations.models import Location
from rapidsms_xforms.models import XFormSubmission
from script.models import ScriptSession
import datetime
from django.utils.safestring import mark_safe
from django.conf import settings
from mcdtrac.utils import \
    get_district_for_facility, \
    get_last_reporting_date, \
    get_facility_reports, \
    reporting_facilities
import calendar
import time
import re

def get_section(path):
    pos = path.split('/')
    return pos[2]

def get_parent(location_id):
    if location_id:
        location = get_object_or_404(Location, pk=location_id)
    else:
        location = Location.tree.root_nodes()[0]
    return location

def breadcrumb(location):
    toret = list(location.get_ancestors())
    toret.append(location)
    return toret

def get_parentId(location_id):
    if location_id:
        location = get_object_or_404(Location, pk=location_id)
    else:
        location = Location.tree.root_nodes()[0]
    return location.parent_id

def get_ancestors(location_id):
    if location_id:
        location = get_object_or_404(Location, pk=location_id)
    else:
        location = Location.tree.root_nodes()[0]
    return location.get_ancestors()

def get_district(location):
    try:
        return location.name if location.type.name == 'district' else location.get_ancestors().get(type__name='district').name
    except:
        return None

def get_facility_district(hc):
    return get_district_for_facility(hc)

def join_date(connection):
    try:
        return ScriptSession.objects.filter(connection=connection, script__slug='cvs_autoreg').latest('end_time').end_time
    except:
        return None


def get_submission_values(submission):
    return submission.eav.get_values().order_by('attribute__xformfield__order')

def name(location):
    return location.name

def latest(obj):
    try:
        return XFormSubmission.objects.filter(connection__in=obj.connection_set.all()).latest('created').created
    except:
        return None

def facility_latest(obj):
    return get_last_reporting_date(obj)

def facility_reports(obj):
    toret = reporting_facilities(None, facilities=[obj], count=False, date_range=None)
    if len(toret):
        return toret[0]['pk__count']
    else:
        return 0

def hash(h, key):
    try:
        val = h[key]
    except KeyError:
        val = None
    return val
month_options = (
    (),
    (1, 'Jan'),
    (2, 'Feb'),
    (3, 'Mar'),
    (4, 'Apr'),
    (5, 'May'),
    (6, 'Jun'),
    (7, 'Jul'),
    (8, 'Aug'),
    (9, 'Sept'),
    (10, 'Oct'),
    (11, 'Nov'),
    (12, 'Dec'),
)

class DateRangeNode(template.Node):

    def __init__(self , min_date, max_date, start_date, end_date):
        self.end_date = template.Variable(end_date)
        self.start_date = template.Variable(start_date)
        self.min_date = template.Variable(min_date)
        self.max_date = template.Variable(max_date)
    def render(self, context):
        try:
            end_date = self.end_date.resolve(context)
            start_date = self.start_date.resolve(context)
            min_date = self.min_date.resolve(context)
            max_date = self.max_date.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        start_date = datetime.datetime.fromtimestamp(start_date / 1000)
        end_date = datetime.datetime.fromtimestamp(end_date / 1000)
        min_date = datetime.datetime.fromtimestamp(min_date / 1000)
        max_date = datetime.datetime.fromtimestamp(max_date / 1000)

        years = range(min_date.year, max_date.year + 1)
        start_opts = \
        """
            <label for='%s'>%s</label>
            <select name='%s' id='%s' style='display:none;'>"""
        for year in years:

            opt_year = "<optgroup label='%s'>" % str(year)
            start_opts = start_opts + opt_year
            if year == min_date.year:
                for month in range(min_date.month, 13):
                    opt_month = "<optgroup label='%s'>" % str(month_options[month][1])
                    start_opts = start_opts + opt_month
                    for day in range(1, calendar.monthrange(year, month)[1] + 1):
                        option = "<option value=%d>%s-%s-%s</option>"\
                     % (time.mktime(datetime.datetime(year, month, day).timetuple()) * 1000, str(day), str(month_options[month][1]), str(year))
                        start_opts = start_opts + option
                    start_opts = start_opts + '</optgroup>'


            elif year == max_date.year:
                for month in range(1, max_date.month + 1):
                    opt_month = "<optgroup label='%s'>" % str(month_options[month][1])
                    start_opts = start_opts + opt_month
                    for day in range(1, calendar.monthrange(year, month)[1] + 1):
                        option = "<option value=%d>%s-%s-%s</option>"\
                     % (time.mktime(datetime.datetime(year, month, day).timetuple()) * 1000, str(day), str(month_options[month][1]), str(year))
                        start_opts = start_opts + option
                    start_opts = start_opts + '</optgroup>'
            else:
                for month in range(1, 13):
                    opt_month = "<optgroup label='%s'>" % str(month_options[month][1])
                    start_opts = start_opts + opt_month
                    for day in range(1, calendar.monthrange(year, month)[1] + 1):
                        option = "<option value=%d>%s-%s-%s</option>"\
                     % (time.mktime(datetime.datetime(year, month, day).timetuple()) * 1000, str(day), str(month_options[month][1]), str(year))
                        start_opts = start_opts + option
                    start_opts = start_opts + '</optgroup>'

            start_opts = start_opts + '</optgroup>'
        start_opts = start_opts + '</select>'
        start_ts = time.mktime(start_date.date().timetuple()) * 1000
        end_ts = time.mktime(end_date.date().timetuple()) * 1000
        start_re = re.compile("<option value=%d>" % start_ts)
        end_re = re.compile("<option value=%d>" % end_ts)
        start_selected_str = "<option value=%d' selected='selected'>" % start_ts
        end_selected_str = "<option value=%d' selected='selected'>" % end_ts
        start_html = start_opts % ('start', '', 'start', 'start')
        end_html = start_opts % ('end', '', 'end', 'end')
        start_html = start_re.sub(start_selected_str, start_html)
        end_html = end_re.sub(end_selected_str, end_html)
        return mark_safe(start_html + end_html)




def do_date_range(parser, token):
	"""
	returns dateranges grouped by month and by week

	"""
	chunks = token.split_contents()
	if not len(chunks) == 5:
		raise template.TemplateSyntaxError, "%r tag requires two arguments" % token.contents.split()[0]

	return DateRangeNode(chunks[1], chunks[2], chunks[3], chunks[4])

#get reporting period for given date
def get_reporting_period(d, period=0, weekday=getattr(settings, 'FIRSTDAY_OF_REPORTING_WEEK', 3)):
    d = datetime.datetime(d.year, d.month, d.day)
    last_thursday = d - datetime.timedelta((((7 - weekday) + d.weekday()) % 7)) - datetime.timedelta((period - 1) * 7)
    return (last_thursday - datetime.timedelta(7), last_thursday)

# returns week# for a given date
def get_reporting_week_number(d):
    first_monday = get_reporting_period(d)[0]
    start_of_year = datetime.datetime(first_monday.year, 1, 1, 0, 0, 0)
    td = first_monday - start_of_year
    toret = int(td.days / 7)
    if start_of_year.weekday() != 0:
        toret += 1
    return toret
#return name for user's excel report
def get_user_report_name(user):
    if user.upper() in ['NMS', 'MU', 'MOH']:
        return 'reports.xls'
    d = Location.objects.filter(name__iexact=user, type='district')
    if len(d) > 0:
        return 'reports_%s.xls' % (user.capitalize())
    return "reports.xls"

def hc(obj):
    return obj.contact.healthprovider.facility.name

register = template.Library()
register.filter('section', get_section)
register.filter('parent', get_parent)
register.filter('parentId', get_parentId)
register.filter('ancestors', get_ancestors)
register.filter('name', name)
register.filter('join_date', join_date)
register.filter('latest', latest)
register.filter('facility_latest', facility_latest)
register.filter('facility_reports', facility_reports)
register.filter('hash', hash)
register.filter('get_district', get_district)
register.filter('get_facility_district', get_facility_district)
register.filter('get_submission_values', get_submission_values)
register.filter('breadcrumb', breadcrumb)
register.filter('reporting_week', get_reporting_week_number)
register.filter('get_user_report_name', get_user_report_name)
register.tag('date_range', do_date_range)
register.filter('hc', hc)
