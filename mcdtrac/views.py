import os
from django.http import HttpResponse, HttpResponseBadRequest
from django.http import Http404
from django.views.decorators.http import require_GET
from django.template import RequestContext
from django.shortcuts import redirect, get_object_or_404, render_to_response
from django.conf import settings
from django.core.management import call_command
from rapidsms_xforms.models import XForm, XFormSubmission
from django.core.paginator import Paginator
from generic.views import generic
from .forms import XFormsForm

mcd_keywords = getattr(settings, 'MCDTRAC_XFORMS_KEYWORDS', ['dpt', 'muac', 'tet', 'anc', 'eid', 'reg', 'me', 'vit', 'worm'])

def save_upload(uploaded, filename, raw_data):
    '''
        raw_data: if True, uploaded is an HttpRequest object with the file being
        the raw post data
        if False, uploaded has been submitted via the basic form
        submission and is a regular Django UploadedFile in request.FILES
    '''
    try:
        from io import FileIO, BufferedWriter
        with BufferedWriter(FileIO(filename, "wb")) as dest:
            # if the "advanced" upload, read directly from the HTTP request
            # with the Django 1.3 functionality
            if raw_data:
                foo = uploaded.read(1024)
                while foo:
                    dest.write(foo)
                    foo = uploaded.read(1024)
            # if not raw, it was a form upload so read in the normal Django chunks fashion
            else:
                for c in uploaded.chunks():
                    dest.write(c)
            # got through saving the upload, report success
            return True
    except IOError:
        # could not open the file most likely
        pass
    return False


def ajax_upload(request):
    if request.method == "POST":
        if request.is_ajax():
            # the file is stored raw in the request
            print "stored raw in request"
            upload = request
            is_raw = True
            # AJAX Upload will pass the filename in the querystring if it is the "advanced" ajax upload
            try:
                filename = request.GET[ 'qqfile' ]
            except KeyError:
                return HttpResponseBadRequest("AJAX request not valid")
        # not an ajax upload, so it was the "basic" iframe version with submission via form
        else:
            is_raw = False
            if len(request.FILES) == 1:
                # FILES is a dictionary in Django but Ajax Upload gives the uploaded file an
                # ID based on a random number, so it cannot be guessed here in the code.
                # Rather than editing Ajax Upload to pass the ID in the querystring,
                # observer that each upload is a separate request,
                # so FILES should only have one entry.
                # Thus, we can just grab the first (and only) value in the dict.
                upload = request.FILES.values()[ 0 ]
            else:
                raise Http404("Bad Upload")
            filename = upload.name

        # save the file
        filename = "/tmp/%s" % filename
        success = save_upload(upload, filename, is_raw)
        call_command("load_reporters", filename)
        # let Ajax Upload know whether we saved it or not
        import json
        ret_json = { 'success': success, }
        return HttpResponse(json.dumps(ret_json))
    
def mcdtrac_xforms(req):
    xforms = XForm.on_site.filter(keyword__in=mcd_keywords)
    breadcrumbs = (('XForms', ''),)
    return render_to_response(
        "xforms/form_index.html",
        { 'xforms': xforms, 'breadcrumbs': breadcrumbs },
        context_instance=RequestContext(req))
    
def view_submissions(req):
    if req.method == 'POST':
        form_id = req.POST.get('form_id') if req.POST.get('form_id') else None
    else:
        form_id = None
        
    xform = XForm.on_site.get(keyword = mcd_keywords[0]) if form_id == None\
         else XForm.on_site.get(pk=form_id)
          
    submissions = xform.submissions.all().order_by('-pk')
    fields = xform.fields.all().order_by('pk')

#    breadcrumbs = (('XForms', '/xforms/'), ('Submissions', ''))
    return generic(
      request = req,
      model = XFormSubmission,
      queryset = submissions,
      filter_forms = [XFormsForm], #, FacilityFilterForm,
      objects_per_page = 25,
      partial_row = 'mcdtrac/submissions/partials/submission_row.html',
      partial_header = 'mcdtrac/submissions/partials/submission_header.html',
      base_template = 'mcdtrac/submissions_base.html',
#      base_template = 'cvs/messages_base.html',
      results_title = 'Submissions for %s' % xform.name,
      columns = [('Name', True, 'name', None)],
      sort_column = 'last_reporting_date',
      sort_ascending = False,
      fields = fields,
      selectable = False,
      submissions = submissions,
      xform = xform,       
            )

#    return render_to_response("mcdtrac/submissions.html",
#                              dict(xform=xform, fields=fields, submissions=page, breadcrumbs=breadcrumbs,
#                                   paginator=paginator, page=page),
#                              context_instance=RequestContext(req))

# CSV Export
@require_GET
def submissions_as_csv(req, pk=None):
    import pdb
    pdb.set_trace()
    xforms = []
    submissions = []
    fields = []
    if pk:
        xforms.append(get_object_or_404(XForm, pk=pk))
    else:
        for kw in mcd_keywords:
            xforms.append(XForm.objects.get(keyword=kw))

    for xform in xforms:
        submissions.append(xform.submissions.all().order_by('-pk'))
        fields.append(xform.fields.all().order_by('pk'))

    resp = render_to_response(
        "mcdtrac/submissions.csv",
        {'xforms': xforms, 'submissions': submissions, 'fields': fields},
        mimetype="text/csv",
        context_instance=RequestContext(req))
    resp['Content-Disposition'] = 'attachment;filename="%s.csv"' % xform.keyword
    return resp
