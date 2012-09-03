from django.db import models
from rapidsms.models import Contact
from healthmodels.models.HealthFacility import HealthFacility
from healthmodels.models.HealthProvider import HealthProvider
from rapidsms_xforms.models import XForm, XFormSubmission
from rapidsms_xforms.models import XFormReport, XFormList, XFormReportSubmission
from rapidsms_xforms.models import xform_received
import datetime
from django.conf import settings

XFORMS = getattr(settings, 'MCDTRAC_XFORMS_KEYWORDS', ['dpt', 'redm', 'tet', 'anc', 'eid', 'breg', 'me', 'vita', 'worm'])

class PoW(models.Model):
    name = models.CharField(max_length=255)
    served_by = models.ForeignKey(HealthFacility)
    
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
#     pow = models.ForeignKey(PoW)

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
    pow = models.ForeignKey(PoW)
    xform_report = models.ForeignKey(XFormReportSubmission)
    modified = models.DateTimeField('Modified On', auto_now=True)
    active = models.BooleanField(default=False)

def check_basic_validity(xform_type, submission, health_provider, day_range):
    xform = XForm.objects.get(keyword=xform_type)
    start_date = datetime.datetime.now() - datetime.timedelta(hours=(day_range * 24))
    for s in XFormSubmission.objects.filter(connection__contact=health_provider,
                                            xform=xform,
                                            created__gte=start_date).exclude(pk=submission.pk):
        s.has_errors = True
        s.save()
            
def mcd_xform_handler(sender, **kwargs):
    xform = kwargs['xform']
    if not xform.keyword in XFORMS:
        return
    submission = kwargs['submission']

    if submission.has_errors:
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

    if xform.keyword in XFORMS:
        check_basic_validity(xform.keyword, submission, health_provider, 1)

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
    
xform_received.connect(mcd_xform_handler, weak=True)

def fhd_start_date():
    """
    returns the report date for this report.
    
    for now i'll set it to the monday of the week when reports are comming in.
    """
    today = datetime.date.today()
    return today - datetime.timedelta(days=today.weekday())
    
##
## XFormReport constraints.
##
# TODO: code to pop these from the XFormReport

def fhd_pow_constraint(sender, **kwargs):
    """
    Each report is by place of worship. This constraint begins a new report.
    
    this constraint is stored in XFormReport.constraints[] to be called bellow.
    
    note that some other reporter may have already entered data for this POW.
    
    we need to:
        1. check if there's any other report for this POW in progress
        2. Create a new report if 1 above is not true
        3. Save the report found by 1 or 2 in our scratch table.
    """
    xform = kwargs['xform']
    submission = kwargs['submission']
    if (not xform.keyword == 'pow') or submission.has_errors:
        return
    
    try:
        health_provider = submission.connection.contact.healthproviderbase.healthprovider
    except:
        submission.response = "You must be a reporter for FHDs. Please register first ebfore sending any information" 
        submission.has_erros = True
        submission.save()
        return
    
    #TODO: re-write to loop through all matching reports...
    try:
         rep_list = XFormList.objects.get(xform = xform)
    except XFormList.MultipleObjectsReturned:
        # you could decide to just loop through each matching form ...
         rep_list = XFormList.objects.filter(xform = xform)[0]
    except XFormList.DoesNotExist:
        submission.response = "This submission has not been added to any FHD report."
        submission.has_errors = True
        submission.save()
        return
    try:
        pow = PoW.objects.get(name=submission.eav.pow_name, served_by=health_provider.facility)
    except PoW.DoesNotExist:
        pow = PoW.objects.create(
                name=submission.eav.pow_name,
                served_by = health_provider.facility
        )
        
    report_submission = None
    for r in XFormReportSubmission.objects.filter(
                                                    status='open',
                                                    submissions__xform__keyword='pow'
                                                ):
        if pow.name == r.submission.eav.pow_name:
            report_submission = r
            break # stop at the first matching - in this case.
    if report_submission is None:
        report_submission = XFormReportSubmission.objects.create(
           report = rep_list.report,
           status = 'open',
           start_date = fhd_start_date())
        report_submission.submissions.add(submission)
        report_submission.save()
    
    # update the xform-report-submissions being worked on if it exists,
    # create a new entry if it doesn't.
    try:
        scratch = ReportsInProgress.objects.get(provider = health_provider, active=True)
    except ReportsInProgress.DoesNotExist:
        scratch = ReportsInProgress.create(
            provider = health_provider,
            pow = pow,
            xform_report = report_submission,
            active = True
        )
    else:
        scratch.pow = pow
        scratch.xform_report = report_submission

def fhd_summary_constraint(sender, **kwargs):
    """
    handle summmary xform sent by in-charge
    
    This constraint is stored in XFormReports.constraints[] (as the first item)
    and is used to signify the end of all reports from this health facility
    """
    
    xform = kwargs['xform']
    submission = kwargs['submission']
    if (not xform.keyword == 'summary') or submission.has_errors:
        return
    
    try:
        health_provider = submission.connection.contact.healthproviderbase.healthprovider
    except:
        submission.response = "You must be a reporter for FHDs. Please register first ebfore sending any information" 
        submission.has_erros = True
        submission.save()
        return

    # TODO: probably add basic checking for PINs.
    
    # TODO: rewrite this as a models.F() single step...
    for pow in PoW.objects.filter(served_by=health_provider.facility):
        for scratch in ReportsInProgress.objects.filter(pow=pow, active=True):
            scratch.xform_report.status = 'closed'
            scratch.active = False

##
## XFormReport general handler
##
def fhd_add_submission_handler(sender, **kwargs):
    """
    add a submission to an xform-report-submission
    """
    
    xform = kwargs['xform']
    submission = kwargs['submission']
    if (not xform.keyword in XFORMS ) or submission.has_errors:
        return

    try:
        health_provider = submission.connection.contact.healthproviderbase.healthprovider
    except:
        submission.response = "You must be a reporter for FHDs. Please register first ebfore sending any information" 
        submission.has_erros = True
        submission.save()
        return

    # reports may be more than one
    try:
         rep_list = XFormList.objects.get(xform = xform)
    except XFormList.MultipleObjectsReturned:
        # you could decide to just loop through each matching form ...
         rep_list = XFormList.objects.filter(xform = xform)[0]
    except XFormList.DoesNotExist:
        submission.response = "This submission has not been added to any FHD report."
        submission.has_errors = True
        submission.save()
        return
           
    try:
        report = ReportsInProgress.objects.get(provider=health_provider, active=True)
    except ReportsInProgress.DoesNotExist:
        submission.response = "Tell me what POW you are reporting for before submitting data."
        return
    
    # append to the report
    report.xform_report.submissions.add(submission)
    report.xform_report.save() # i may not need this

xform_received.connect(fhd_add_submission_handler, weak=True)