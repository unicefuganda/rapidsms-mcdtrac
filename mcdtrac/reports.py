from django.conf import settings
from django.db.models import Count, Sum
from generic.reports import Column as Col, Report
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

from generic.reporting.views import ReportView
from generic.reporting.reports import Column
from uganda_common.views import XFormReport

class FHDMixin(object):
    """
    Mixins for COlumn objects bellow for similar functionality.
    """
    LOCATION_ID = 'submission__connection__contact__healthproviderbase__healthprovider__reporting_location__pk'
    LOCATION_NAME = 'submission__connection__contact__healthproviderbase__healthprovider__reporting_location__name'

    def total_attribute_by_location(self, report, keyword, single_week=False):
        print report.location
        start_date = report.start_date
        if single_week:
            start_date = report.end_date - datetime.timedelta(7)
        #import pdb; pdb.set_trace()
        return XFormSubmissionValue.objects.exclude(submission__has_errors=True)\
            .exclude(submission__connection__contact=None)\
            .filter(created__range=(start_date, report.end_date))\
            .filter(attribute__slug__in=keyword)\
            .filter(submission__connection__contact__healthproviderbase__healthprovider__reporting_location__in=report.location.get_descendants(include_self=True).all())\
            .values(self.LOCATION_NAME,
                    self.LOCATION_ID)\
            .annotate(Sum('value_int'))


    def total_dateless_attribute_by_school(self, report, keyword):
        return XFormSubmissionValue.objects.exclude(submission__has_errors=True)\
            .exclude(submission__connection__contact=None)\
            .filter(attribute__slug__in=keyword)\
            .filter(submission__connection__contact__emisreporter__schools__location__in=report.location.get_descendants(include_self=True).all())\
            .values(self.SCHOOL_NAME,
                    self.SCHOOL_ID)\
            .annotate(Sum('value_int'))


    def num_weeks(self, report):
        if report.end_date == report.start_date:
            report.end_date = report.end_date + datetime.timedelta(days=1)
        td = report.end_date - report.start_date
        holidays = getattr(settings, 'SCHOOL_HOLIDAYS', [])
        for start, end in holidays:
            if start > report.start_date and end < report.end_date:
                td -= (end - start)

#        return td.days / 7
        return td.days / 7 if td.days / 7 > 1 else 1

class FHDReportColumn(Col, FHDMixin):
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
        print val
        # num_weeks = self.num_weeks(report)
        # for rdict in val:
        #     rdict['value_int__sum'] /= num_weeks
        # import pdb; pdb.set_trace()
        reorganize_dictionary(key, val, dictionary, self.LOCATION_ID, self.LOCATION_NAME, 'value_int__sum')


class FHDReportBase(Report):

    def __init__(self, request, dates):
        try:
            self.location = get_location_for_user(request.user)
        except:
            pass
        if self.location is None:
            self.location = Location.tree.root_nodes()[0]
        Report.__init__(self, request, dates)

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
# class AttendanceReport(XFormReport):
#     boys = WeeklyAttributeBySchoolColumn(["boys_%s" % g for g in GRADES])
#     girls = WeeklyAttributeBySchoolColumn(["girls_%s" % g for g in GRADES])
#     total_students = WeeklyAttributeBySchoolColumn((["girls_%s" % g for g in GRADES] + ["boys_%s" % g for g in GRADES]))
#     percentage_students = AverageWeeklyTotalRatioColumn((["girls_%s" % g for g in GRADES] + ["boys_%s" % g for g in GRADES]), (["enrolledg_%s" % g for g in GRADES] + ["enrolledb_%s" % g for g in GRADES]))
#     week_attrib = ["girls_%s" % g for g in GRADES] + ["boys_%s" % g for g in GRADES]
#     total_attrib = ["enrolledb_%s" % g for g in GRADES] + ["enrolledg_%s" % g for g in GRADES]
#     percentange_student_absentism = WeeklyPercentageColumn(week_attrib, total_attrib, True)
#     male_teachers = WeeklyAttributeBySchoolColumn("teachers_m")
#     female_teachers = WeeklyAttributeBySchoolColumn("teachers_f")
#     total_teachers = WeeklyAttributeBySchoolColumn(["teachers_f", "teachers_m"])
#     percentage_teacher = AverageWeeklyTotalRatioColumn(["teachers_f", "teachers_m"], ["deploy_f", "deploy_m"])
#     week_attrib = ["teachers_f", "teachers_m"]
#     total_attrib = ["deploy_f", "deploy_m"]
#     percentange_teachers_absentism = WeeklyPercentageColumn(week_attrib, total_attrib, True)
