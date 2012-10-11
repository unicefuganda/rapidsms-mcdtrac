from django.conf import settings
from django.db.models import Count, Sum
from generic.reports import Column, Report
from generic.utils import flatten_list
from rapidsms.contrib.locations.models import Location
from rapidsms_httprouter.models import Message
from django.db.models import Q
from script.models import Script
from rapidsms_xforms.models import XFormSubmissionValue, XForm, XFormSubmission
from uganda_common.reports import XFormSubmissionColumn, XFormAttributeColumn, PollNumericResultsColumn, PollCategoryResultsColumn, LocationReport, QuotientColumn, InverseQuotientColumn
from uganda_common.utils import total_submissions, reorganize_location, total_attribute_value, previous_calendar_month
from uganda_common.utils import reorganize_dictionary
from poll.models import Response, Poll
from .utils import previous_calendar_week, get_location_for_user
import datetime
from django.db.models.sql.constants import *

from generic.reporting.views import ReportView
from uganda_common.views import XFormReport

class FHDMixin(object):
    """
    Mixins for Column objects bellow for similar functionality.

    TODO: merge with the FHDReportColumn since we only have one type of Column
    """

    def total_attribute_by_location(self, report, keyword, single_week=False):
        print report.location
        start_date = report.start_date
        end_date = report.end_date
        if single_week:
            start_date = end_date - datetime.timedelta(7)

        # ## from django.db.models.sql.constants import *
        # ## defined in the import above ... RHS_ALIAS = 1
        # q = XFormSubmissionValue.objects.exclude(
        #         submission__connection__contact=None
        #     ).filter(
        #         submission__has_errors=False,
        #         attribute__slug__in=keyword,
        #         submission__created__lte=end_date,
        #         submission__created__gte=start_date
        #     ).values(
        #         'submission__connection__contact__healthproviderbase__healthprovider__reporting_location__name'
        #     )
        # repr(q.extra(tables=['locations_location']))  ## force queryset to be evaluated
        # alias = q.query.table_map['locations_location'][RHS_ALIAS]
        # print alias  ## debug

        alias = 'T12'

        if report.location.get_children().count() > 1:
            location_children_where = '{0}.id in {1}'.format(
                    alias, str(
                                tuple(
                                    report.location.get_children().values_list('pk', flat=True)
                                )
                            )
            )
        else:
            location_children_where = '{0}.id in {1}'.format(
                    alias, report.location.get_children()[0].pk
            )

        return list(XFormSubmissionValue.objects.exclude(
                submission__connection__contact=None
            ).filter(
                submission__has_errors=False,
                attribute__slug__in=keyword,
                submission__created__lte=end_date,
                submission__created__gte=start_date
            ).values(
                'submission__connection__contact__healthproviderbase__healthprovider__reporting_location__name'
            ).extra(
                tables=['locations_location'],
                where=[
                    '{0}.lft <= locations_location.lft'.format(alias),
                    '{0}.rght >= locations_location.rght'.format(alias),
                    location_children_where
                ],
                select={
                    'location_name': '{0}.name'.format(alias),
                    'location_id': '{0}.id'.format(alias),
                    'rght': '{0}.rght'.format(alias),
                    'lft': '{0}.lft'.format(alias)
                }
            ).values(
                'location_name', 'location_id', 'lft', 'rght'
            ).annotate(
                value=Sum('value_int')
            # ).extra(
            #     order_by=['location_name']
            )
        )

class FHDReportColumn(Column, FHDMixin):
    """
    Return the values for a particular column (male/female)
    generic will use the add_to_report function to create the report dictionary
    """

    def __init__(self, keyword, location=None, extra_filters=None):
        if type(keyword) != list:
            keyword = [keyword]
        self.keyword = keyword
        self.extra_filters = extra_filters

    def add_to_report(self, report, key, dictionary):
        val = self.total_attribute_by_location(report, self.keyword)
        # print val  ## debug
        # print key  ## debug
        # reorganize_dictionary(key, val, dictionary, 'location_id', 'location_name', 'value')
        reorganize_location(key, val, dictionary)


class FHDReportBase(Report):

    drill_to_facility = False

    def __init__(self, request, dates):
        try:
            self.location_root = get_location_for_user(request.user)
        except:
            pass
        if self.location_root is None:
            self.location_root = Location.tree.root_nodes()[0]
        try:
            self.drill_on(int(request.POST['drill_key']))
        except:
            self.location = self.location_root
        Report.__init__(self, request, dates)

    def drill_on(self, key):
        #print "drilling on {0}".format(int(key)) # debug
        try:
            self.location = Location.objects.get(pk=int(key))
        except:
            self.location = self.location_root
        while self.location.get_children().count() == 1 and not self.location.type == 'sub_county':
            # drill again as long as there's only one child
            self.location = self.location.get_children[0]

        if self.location.type.name == 'sub_county':
            self.drill_to_facility = True

class FHDReport(FHDReportBase):
    dpt_male = FHDReportColumn(['dpt_male'])
    dpt_female = FHDReportColumn(['dpt_female'])
    vacm_male = FHDReportColumn(['vacm_male'])
    vacm_female = FHDReportColumn(['vacm_female'])
    vita_male1 = FHDReportColumn(['vita_male1'])
    vita_female1 = FHDReportColumn(['vita_female1'])
    vita_male2 = FHDReportColumn(['vita_male2'])
    vita_female2 = FHDReportColumn(['vita_female2'])
    worm_male = FHDReportColumn(['worm_male'])
    worm_female = FHDReportColumn(['worm_female'])
    redm_number = FHDReportColumn(['redm_number'])
    tet_dose2 = FHDReportColumn(['test_dose2'])
    tet_dose3 = FHDReportColumn(['test_dose3'])
    tet_dose4 = FHDReportColumn(['test_dose4'])
    tet_dose5 = FHDReportColumn(['test_dose5'])
    anc_number = FHDReportColumn(['anc_number'])
    eid_male = FHDReportColumn(['eid_male'])
    eid_female = FHDReportColumn(['eid_female'])
    breg_male = FHDReportColumn(['breg_male'])
    breg_female = FHDReportColumn(['breg_female'])
