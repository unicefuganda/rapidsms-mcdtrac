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
    url(r'^mcdtrac/', login_required(view_submissions), name='mcds'),
    url(r'^mcdtrac/xforms/$', login_required(mcdtrac_xforms), name='mcd-xforms'),
    url(r'^mcdtrac/(\d+)/submissions/$', login_required(view_submissions), name='mcd-submissions'),
    
)