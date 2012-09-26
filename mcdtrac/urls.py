from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.auth.decorators import login_required
from generic.views import *
from generic.sorters import *
from contact.forms import *
from contact.utils import get_messages
from healthmodels.models.HealthProvider import HealthProviderBase
from .utils import *
from .views import view_submissions, mcdtrac_xforms, submissions_as_csv
from .sorters import LatestSubmissionSorter
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    url(r'^mcdtrac/dhts/$', direct_to_template, {'template': 'stats.html'} ),
    url(r'^mcdtrac/', login_required(view_submissions), name='mcds'),
    url(r'^mcdtrac/xforms/$', login_required(mcdtrac_xforms), name='mcd-xforms'),
    url(r'^mcdtrac/(?P<form_id>\d+)/submissions/$', login_required(view_submissions), name='mcd-submissions'),
    #Export CSV
    url(r"^mcdtrac/submissions.csv$", login_required(submissions_as_csv), name='mcd-all-excel'),
    url(r"^mcdtrac/(?P<pk>\d+)/submissions.csv$", login_required(submissions_as_csv), name='mcd-excel')
    
)