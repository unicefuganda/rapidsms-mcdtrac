from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.auth.decorators import login_required
from generic.views import *
from generic.sorters import *
from contact.forms import *
from contact.utils import get_messages

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
    
)