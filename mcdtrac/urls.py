from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.auth.decorators import login_required
from generic.views import *
from generic.sorters import *
from contact.forms import *
from contact.utils import get_messages
from healthmodels.models.HealthProvider import HealthProviderBase
from .utils import *
from .views import *
from .sorters import LatestSubmissionSorter

urlpatterns = patterns('',
    url(r'^$', login_required(generic), {
      'model':Message,
      'queryset':get_messages,
      'filter_forms':[FreeSearchTextForm, DistictFilterMessageForm],
      'action_forms':[ReplyTextForm, FlagMessageForm],
      'objects_per_page':25,
      'partial_row':'contact/partials/message_row.html',
      'base_template':'contact/messages_base.html',
      'columns':[('Text', True, 'text', SimpleSorter()),
                 ('Contact Information', True, 'connection__contact__name', SimpleSorter(),),
                 ('Date', True, 'date', SimpleSorter(),),
                 ('Type', True, 'application', SimpleSorter(),),
                 ('Response', False, 'response', None,),
                 ],
      'sort_column':'date',
      'sort_ascending':False,
    }, name="rapidsms-dashboard"),
                       
    #############################################
   #              REPORTERS VIEWS              #
   #############################################
   # Registered Users
    url(r'^mcdtrac/reporter/$', login_required(generic), {
      'model':HealthProviderBase,
      'queryset':get_reporters,
      'filter_forms':[FreeSearchForm, DistictFilterForm, RolesFilter], #, FacilityFilterForm,
      'action_forms':[MassTextForm], #, DeactivateForm
      'objects_per_page':25,
      'partial_row':'mcdtrac/reporter/partials/reporter_row.html',
      'partial_header':'mcdtrac/reporter/partials/partial_header.html',
      'base_template':'contact/messages_base.html',
#      'base_template':'mcdtrac/reporter/registered_contacts.html',
      'results_title':'Registered Users',
      'columns':[('Name', True, 'name', SimpleSorter()),
                 ('Number', True, 'connection__identity', SimpleSorter(),),
                 ('Role(s)', True, 'groups__name', SimpleSorter(),),
                 ('District', False, 'district', None,),
                 ('Last Reporting Date', True, 'last_reporting_date', LatestSubmissionSorter(),),
                 ('Total Reports', True, 'connection__submissions__count', SimpleSorter(),),
                 ('Facility', True, 'facility__name', SimpleSorter(),),
                 ('Location', True, 'location__name', SimpleSorter(),),
                 ('Active', True, 'active', SimpleSorter(),),
                 ('', False, '', None,)],
      'sort_column':'last_reporting_date',
      'sort_ascending':False,
    }, name="mcd-contact"),
                       
    url(r'^ajax_upload/$', ajax_upload, name="ajax_upload"),
    
)