from django.db import models
from rapidsms.models import Contact
from healthmodels.models import HealthFacility

class PoW(models.Model):
    name = models.CharField(max_length=255)
    served_by = models.ForeignKey(HealthFacility)
    
    def __unicode__(self):
        return '%s' % self.name
    
class Reporter(Contact):
    sites_of_operation = models.ManyToManyField(PoW, through='ReporterPoW')
    
    def __unicode__(self):
        return '%s %s' % self.name, self.connection
    
class ReporterPoW(models.Model):
    reporter = models.ForeignKey(Reporter)
    pow = models.ForeignKey(PoW)
    