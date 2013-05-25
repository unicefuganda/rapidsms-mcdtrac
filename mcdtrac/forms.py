from django.conf import settings
from django import forms
from rapidsms_xforms.models import XForm
from generic.forms import ActionForm, FilterForm
from .utils import XFORMS

mcd_keywords = XFORMS

class XFormsForm(FilterForm):
    xform_id = forms.ChoiceField(label="XForm", choices=(('', '-----'),) + tuple([(int(xf.pk),
                                 xf.name) for xf in
                                 XForm.on_site.filter(keyword__in=mcd_keywords)]),
                                 required=False,
                                 widget=forms.Select({'onchange':'select_xform(this);'}))


    def filter(self, request, queryset):
        xform_id = self.cleaned_data['xform_id']
        if xform_id == '':
            return queryset
        else:
            return queryset.filter(pk=xform_id)
