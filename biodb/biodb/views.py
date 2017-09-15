from django.views.generic import View
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

class RedirectView(View):
    def get(self, request, **kwargs):
        if request.user.is_authenticated():
            return redirect(reverse("projects:projects_list"))
        else:
            return redirect(reverse("login"))
