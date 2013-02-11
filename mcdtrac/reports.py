from django.db.models import Sum
from django.db import connection, transaction
from generic.reports import Column, Report
from rapidsms.contrib.locations.models import Location
from rapidsms_xforms.models import XFormSubmissionValue
from uganda_common.utils import  reorganize_location
from .utils import get_location_for_user, dictfetchall
import datetime

class FHDMixin(object):
    """
    Mixins for Column objects bellow for similar functionality.

    """
    def materialized_attribute_by_location(self, report, keyword, fx='SUM', single_week=False):
        start_date = report.start_date
        end_date = report.end_date
        cursor = connection.cursor()
        if fx == 'COUNT':
            distinct = 'DISTINCT'
        else:
            distinct = ''

        if single_week:
            start_date = end_date - datetime.timedelta(7)

        if report.location.get_children().count() > 1:
            location_children_where = 'l.id in {0}'.format(
                str(tuple(
                    report.location.get_children().values_list('pk', flat=True)
                ))
            )
        else:
            location_children_where = 'l.id = {0}'.format(
                    report.location.get_children()[0].pk
            )

        sql = """SELECT {0}({1} "{2}") AS value,
       l.lft,
       l.id AS location_id,
       l.name AS location_name,
       l.rght
FROM fhd_stats_mview f,
     locations_location l
WHERE f.has_errors = FALSE
    AND f.created >= %s
    AND f.created <= %s
    AND l.lft <= f.lft
    AND l.rght >= f.rght
    AND {3}
GROUP BY l.lft,
         l.id,
         l.name,
         l.rght""".format(fx, distinct, keyword, location_children_where)
        cursor.execute(
            sql, [start_date, end_date])
        rows = dictfetchall(cursor)
        transaction.commit_unless_managed()
        return rows

    def total_attribute_by_location(self, report, keyword, single_week=False):
        #print report.location  # debug
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

class FHDReportMaterializedCol(Column, FHDMixin):
    """
    Pick a single value for a column in the fhd_stats_mview table
    """

    def __init__(self, keyword, fx=None, location=None, extra_filters=None):
        if type(keyword) in [list, tuple]:
            keyword = keyword[0]
        self.keyword = str(keyword).replace('"', '')
        self.extra_filters = extra_filters
        if fx and fx.upper() in ('SUM', 'COUNT'):
            self.fx = fx.upper()
        else:
            self.fx = None

    def add_to_report(self, report, key, dictionary):
        if self.fx:
            val = self.materialized_attribute_by_location(report, self.keyword, self.fx)
        else:
            val = self.materialized_attribute_by_location(report, self.keyword)
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
        self.location = Location.objects.get(pk=int(key))
        while self.location.get_children().count() == 1 and not self.location.type == 'sub_county':
            # drill again as long as there's only one child
            self.location = self.location.get_children()[0]

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
    tet_dose2 = FHDReportColumn(['tet_dose2'])
    tet_dose3 = FHDReportColumn(['tet_dose3'])
    tet_dose4 = FHDReportColumn(['tet_dose4'])
    tet_dose5 = FHDReportColumn(['tet_dose5'])
    anc_number = FHDReportColumn(['anc_number'])
    eid_male = FHDReportColumn(['eid_male'])
    eid_female = FHDReportColumn(['eid_female'])
    breg_male = FHDReportColumn(['breg_male'])
    breg_female = FHDReportColumn(['breg_female'])

class FHDMaterializedReport(FHDReportBase):
    entries = FHDReportMaterializedCol('xformreportsubmission_id', 'COUNT')
    dpt_male = FHDReportMaterializedCol('dpt_male')
    dpt_female = FHDReportMaterializedCol('dpt_female')
    vacm_male = FHDReportMaterializedCol('vacm_male')
    vacm_female = FHDReportMaterializedCol('vacm_female')
    vita_male1 = FHDReportMaterializedCol('vita_male1')
    vita_female1 = FHDReportMaterializedCol('vita_female1')
    vita_male2 = FHDReportMaterializedCol('vita_male2')
    vita_female2 = FHDReportMaterializedCol('vita_female2')
    worm_male = FHDReportMaterializedCol('worm_male')
    worm_female = FHDReportMaterializedCol('worm_female')
    redm_number = FHDReportMaterializedCol('redm_number')
    tet_dose2 = FHDReportMaterializedCol('tet_dose2')
    tet_dose3 = FHDReportMaterializedCol('tet_dose3')
    tet_dose4 = FHDReportMaterializedCol('tet_dose4')
    tet_dose5 = FHDReportMaterializedCol('tet_dose5')
    anc_number = FHDReportMaterializedCol('anc_number')
    eid_male = FHDReportMaterializedCol('eid_male')
    eid_female = FHDReportMaterializedCol('eid_female')
    breg_male = FHDReportMaterializedCol('breg_male')
    breg_female = FHDReportMaterializedCol('breg_female')
