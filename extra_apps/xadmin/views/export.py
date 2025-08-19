from xadmin.views.base import ModelAdminView, filter_hook, csrf_protect_m
from django.db import transaction
from django.http.response import HttpResponseRedirect


class ExportAdminView(ModelAdminView):
    
    def init_request(self, *args, **kwargs):
        return True
    
    @filter_hook
    def post_response(self):
        pass
    
    @csrf_protect_m
    @transaction.atomic
    @filter_hook
    def post(self, request):
        response = self.post_response()
        cls_str = str
        if isinstance(response, cls_str):
            response = HttpResponseRedirect(response)
        return response
