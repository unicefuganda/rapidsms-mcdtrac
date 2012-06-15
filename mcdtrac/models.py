from django.db import models
from rapidsms.models import Contact
from healthmodels.models.HealthFacility import HealthFacility
from healthmodels.models.HealthProvider import HealthProvider
from rapidsms_xforms.models import XForm, XFormSubmission
from rapidsms_xforms.models import xform_received
import datetime
from django.conf import settings

XFORMS = getattr(settings, 'MCDTRAC_XFORMS_KEYWORDS', ['dpt', 'redm', 'tet', 'anc', 'eid', 'breg', 'me', 'vita', 'worm'])

class PoW(models.Model):
    name = models.CharField(max_length=255)
    served_by = models.ForeignKey(HealthFacility)
    
    def __unicode__(self):
        return '%s' % self.name
    
class Reporter(HealthProvider):
    sites_of_operation = models.ManyToManyField(PoW, through='ReporterPoW')
    
    def __unicode__(self):
        return '%s %s' % self.name, self.connection
    
class ReporterPoW(models.Model):
    reporter = models.ForeignKey(Reporter)
    pow = models.ForeignKey(PoW)


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
            submission.response = "You must be a reporter for MCDs. Please register first before sending any information"
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
    