from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.auth.decorators import login_required
from generic.views import *
from generic.sorters import *
from contact.forms import *
from contact.utils import get_messages
from healthmodels.models.HealthProvider import HealthProviderBase
from .utils import *
from .views import view_submissions, mcd_dashboard, mcdtrac_xforms, submissions_as_csv
from .sorters import LatestSubmissionSorter
from django.views.generic.simple import direct_to_template
from .reports import FHDReport

urlpatterns = patterns('',
    url(r'^mcdtrac/demo$', login_required(mcd_dashboard), name='mcds'),
    url(r'^mcdtrac/dhts/$', direct_to_template, {'template': 'stats.html'} ),
    url(r'^mcdtrac/messages/?$', login_required(view_submissions), name='mcds'),
    url(r'^mcdtrac/xforms/$', login_required(mcdtrac_xforms), name='mcd-xforms'),
    url(r'^mcdtrac/(?P<form_id>\d+)/submissions/$', login_required(view_submissions), name='mcd-submissions'),
    #Export CSV
    url(r"^mcdtrac/submissions.csv$", login_required(submissions_as_csv), name='mcd-all-excel'),
    url(r"^mcdtrac/(?P<pk>\d+)/submissions.csv$", login_required(submissions_as_csv), name='mcd-excel'),
    url(r'^mcdtrac/fhdstats/$', login_required(generic), {
        'model':XFormSubmission,
        'queryset':FHDReport,
        'selectable':False,
        'paginated':False,
        'results_title':None,
        'top_columns':[
            #('', 1, None),
            ('DPT', 2, None),
            ('VACM', 2, None),
            ('VITA', 4, None),
            ('WORM', 2, None),
            ('REDM', 1, None),
            ('TET', 4, None),
            ('ANC', 1, None),
            ('EID', 2, None),
            ('BREG', 2, None),
        ],
        'columns':[
            #('', False, '', None),
            ('M', False, 'dpt_male', None),
            ('F', False, 'dpt_female', None),
            ('M', False, 'vacm_male', None),
            ('F', False, 'vacm_female', None),
            ('M\n(6-11 m)', False, 'vita_male1', None),
            ('F\n(6-11 m)', False, 'vita_female1', None),
            ('M\n(12-59 m)', False, 'vita_male2', None),
            ('F\n(12-59 m)', False, 'vita_female2', None),
            ('M', False, 'worm_male', None),
            ('F', False, 'worm_female', None),
            ('', False, 'redm_number', None),
            ('D2', False, 'tet_dose2', None),
            ('D3', False, 'tet_dose3', None),
            ('D4', False, 'tet_dose4', None),
            ('D5', False, 'tet_dose5', None),
            ('', False, 'anc_number', None),
            ('M', False, 'eid_male', None),
            ('F', False, 'eid_female', None),
            ('M', False, 'breg_male', None),
            ('F', False, 'breg_female', None)
        ],
        'partial_row':'mcdtrac/partials/fhd_stats_row.html',
        'partial_header':'mcdtrac/partials/fhd_stats_header.html',
        'base_template':'mcdtrac/fhd_timeslider_base.html',
        'needs_date':True,
        'dates':get_xform_dates,
        'embbed_time_slider': True,
        'has_chart': False,
    }, name='fhd-stats'),

)
