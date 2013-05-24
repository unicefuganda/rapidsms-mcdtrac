from django.db import models
from healthmodels.models.HealthFacility import HealthFacility
from healthmodels.models.HealthProvider import HealthProvider
from rapidsms.contrib.locations.models import Location
from rapidsms_xforms.models import XForm, XFormSubmission
from rapidsms_xforms.models import XFormReport, XFormReportSubmission
from rapidsms_xforms.models import xform_received
import datetime
from django.conf import settings
from .utils import last_reporting_period, OLD_XFORMS, XFORMS

class PoW(models.Model):
    POW_CHOICES = (
        ('01', 'Catholic'),
        ('02', 'Church Of Uganda'),
        ('03', 'Moslem'),
        ('04', 'Other')
    )
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=2, choices=POW_CHOICES)
    served_by = models.ForeignKey(HealthFacility)
    district = models.ForeignKey(Location, blank=True, null=True)

    def __unicode__(self):
        return '%s' % self.name

# class Reporter(HealthProvider):
#     sites_of_operation = models.ManyToManyField(PoW, through='ReporterPoW')
#
#     def __unicode__(self):
#         return '%s %s' % self.name, self.connection
#
# class ReporterPoW(models.Model):
#     reporter = models.ForeignKey(Reporter)
#     place_of_worship = models.ForeignKey(PoW)

class ReportsInProgress(models.Model):
    """
    Keep track of which reports are being submitted by who for which POW(s)

    Since this information changes sporadically, this is just for the
    handlers to know which XFormReportSubmission a given Reporter's
    XFormSubmissions belong to.

    The handler that "closes" reports for the HealthFacility should clean
    out this table.
    """
    provider = models.ForeignKey(HealthProvider)
    place_of_worship = models.ForeignKey(PoW)
    xform_report = models.ForeignKey(XFormReportSubmission)
    modified = models.DateTimeField('Modified On', auto_now=True)
    state = models.CharField(max_length=255, null=True, blank=True)

def check_basic_validity(xform_type, submission, health_provider, day_range, report_in_progress):
    if xform_type in ['sum', 'summary', 'pow']:  # these are just markers
        return
    xform = XForm.objects.get(keyword=xform_type)  # any reason for not just passing the xform to this function?
    start_date = datetime.datetime.now() - datetime.timedelta(hours=(day_range * 24))
    for s in XFormSubmission.objects.filter(connection__contact__healthproviderbase__healthprovider__facility=health_provider.facility,
                                            xform=xform,
                                            created__gte=start_date,
                                            xformreportsubmission__pk=report_in_progress.xform_report.pk
                                            ).exclude(pk=submission.pk):
        s.has_errors = True
        s.save()

##
## XFormReport constraints.
##

def fhd_pow_constraint(xform, submission, health_provider):
    """
    Each report is by place of worship. This constraint begins a new report.

    this constraint is stored in XFormReport.constraints[] to be read from the DB above.

    note that some other reporter may have already entered data for this POW.

    we need to:
        1. check if there's any other report for this POW in progress
        2. Create a new report_submission if 1 above is not true
        3. Save the report found by 1 or 2 in our scratch table.
    """
    if (xform.keyword != 'pow') or submission.has_errors:
        return
    xform_report = XFormReport.objects.get(name='FHD')
    place_of_worship, new_pow = PoW.objects.get_or_create(name=submission.eav.pow_name,
                                                 served_by=health_provider.facility)
    ## look for any report_submissions open for this pow by this health center (there should be at most one)
    rs = XFormReportSubmission.objects.filter(
                                status='open',
                                submissions__xform__keyword='pow',
                                submissions__eav_values__value_text=place_of_worship.name,
                                submissions__connection__contact__healthproviderbase__healthprovider__facility=health_provider.facility
                            ).distinct('pk')
#                                submissions__connection__contact__healthproviderbase__healthprovider__facility=health_provider.facility
#                            ).distinct(XFormReportSubmission.pk)
    if rs.count() == 0:
        report_submission = XFormReportSubmission.objects.create(
                                status='open',
                                report=xform_report,
                                start_date=last_reporting_period(period=0)[0])
    elif rs.count() == 1:
        report_submission = rs[0]
    else:
        raise RuntimeError('Found more XFormReportSubmission objects than we expected: {0}'.format(rs.count()))
    report_in_progress, new_rip = ReportsInProgress.objects.get_or_create(
                                provider=health_provider,
                                state__endswith='editing',  # allows us to swap btn the current and paused
                                place_of_worship=place_of_worship,
                                defaults={'xform_report': report_submission,
                                          'state': 'actively_editing'})
    ## update report_in_progress with what we know
    if new_rip:
        for old_rip in ReportsInProgress.objects.filter(
                                provider=health_provider,
                                state='actively_editing').exclude(pk=report_in_progress.pk):
            old_rip.state = 'paused_editing'
            old_rip.save()
    else:
        report_in_progress.xform_report = report_submission  # shouldn't need this
        report_in_progress.state = 'actively_editing'
        report_in_progress.place_of_worship = place_of_worship  # shouldn't need this
        report_in_progress.save()
    submission.response = 'Your reported POW, {0}, has been set. Please send the data for this POW.'.format(place_of_worship.name)
    submission.save()
    ## add the submission to the reportsubmission.
    report_submission.submissions.add(submission)
    report_submission.save()

def fhd_summary_constraint(xform, submission, health_provider):
    """
    handle summmary xform sent by in-charge

    This constraint is stored in XFormReports.constraints[] (as the first item)
    and is used to signify the end of all reports from this health facility
    """
    if (not xform.keyword in ['sum', 'summary']) or submission.has_errors:
        return
    # TODO: probably add basic checking for PINs.
    # TODO: rewrite this as a models.F() single step...
    for place_of_worship in PoW.objects.filter(served_by=health_provider.facility):
        for scratch in ReportsInProgress.objects.filter(place_of_worship=place_of_worship, state__endswith='editing'):
            scratch.xform_report.status = 'closed'
            scratch.xform_report.save()
            scratch.state = 'closed'
            scratch.save()
    submission.response = "All POW reports for facility {0} have been marked as closed.".format(health_provider.facility)
    submission.save()

##
## Listner to django signal when xforms are received
##

def fhd_xform_handler(sender, **kwargs):
    xform = kwargs['xform']
    if not xform.keyword in XFORMS + OLD_XFORMS:
        return
    submission = kwargs['submission']
    if submission.has_errors:
        return
    if xform.keyword in OLD_XFORMS:
        submission.response = "Hello. You are using the old FHD form. Please contact your DHT for the updated FHD forms. Thanks."
        submission.has_errors = True
        submission.save()
        return
    # TODO: check validity
    kwargs.setdefault('message', None)
    message = kwargs['message']
    try:
        message = message.db_message
        if not message:
            return
    except AttributeError:
        return
    try:
        health_provider = submission.connection.contact.healthproviderbase.healthprovider
    except:
        if xform.keyword in XFORMS:
            submission.response = "You must be a reporter for FHDs. Please register first before sending any information"
            submission.has_errors = True
            submission.save()
        return
    ## 1.0 -> check if there's an open report (pow was sent before)
    if not xform.keyword in ['pow', 'sum', 'summary']:
        try:
            report_in_progress = ReportsInProgress.objects.get(provider=health_provider, state='actively_editing')
        except ReportsInProgress.DoesNotExist:
            submission.response = "Please tell us what POW you are reporting for before submitting data."
            submission.has_errors = True
            submission.save()
            return
    ## 2. -> process the  xforms for validity
    if xform.keyword in XFORMS and not (xform.keyword in ['pow']):
        check_basic_validity(xform.keyword, submission, health_provider, 1, report_in_progress)
        value_list = []
        for v in submission.eav.get_values().order_by('attribute__xformfield__order'):
            value_list.append("%s %d" % (v.attribute.name, v.value_int))
        if len(value_list) > 1:
            value_list[len(value_list) - 1] = " and %s" % value_list[len(value_list) - 1]
        health_provider.last_reporting_date = datetime.datetime.now().date()
        health_provider.save()
        try:
            health_provider.facility.last_reporting_date = datetime.datetime.now().date()
            health_provider.facility.save()
        except:
            pass
        submission.response = "You reported %s.If there is an error,please resend." % ','.join(value_list)
        submission.save()
    if xform.keyword in XFORMS and \
        not (submission.connection.contact and submission.connection.contact.active):
        submission.has_errors = True
        submission.save()
        return
    ## 3. -> add xforms to xformreport
    # append to the report
    if not xform.keyword in ['pow', 'sum', 'summary']:
        report_in_progress.xform_report.submissions.add(submission)
        report_in_progress.xform_report.save()  # i may not need this
        submission.save()
    else:
        ## 4. -> process constraints from the DB (pow handler and sum handler)
        constraints = { 'fhd_pow_constraint': fhd_pow_constraint,
                        'fhd_summary_constraint': fhd_summary_constraint}
        for c in XFormReport.objects.get(name='FHD').constraints:
            # WARNING: I'm (intentionally) not catching KeyError exceptions so all constraints must exist
            constraints[c](xform, submission, health_provider)

xform_received.connect(fhd_xform_handler, weak=True)
