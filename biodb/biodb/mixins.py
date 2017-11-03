from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from biodb import settings
import re


class LoginRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)

        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))


class LoginPermissionRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            permission_obj = self.get_permission_object()
            for permission in self.permissions_required:
                if not request.user.has_perm("projects." + permission, permission_obj):
                    _permission = permission.replace('_', ' ')
                    return HttpResponseForbidden(
                        f"<h1>User doesn't have permission: {_permission}</h1>")
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))


class BreadcrumbsMixin(object):
    breadcrumb_model = "<unknown model>"
    breadcrumb_action = "<unknown action>"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context.update({
            "breadcrumbs": self.get_breadcrumbs()
        })
        return context

    def get_urls_patterns(self):
        url_patterns = [
            {
                "pattern": "^/projects/",
                "title": "projects list"
            },
            {
                "pattern": "^/projects/\w+/",
                "title": "robjects list"
            },
            {
                "pattern": "^/projects/\w+/(samples|tags)/",
                "title": f"{self.breadcrumb_model} list"
            },
            {
                "pattern": "^/projects/\w+/(samples|tags)/\d+/$",
                "title": f"{self.breadcrumb_model} details"
            },
            {
                "pattern": "^/projects/.+/(create|delete|edit)/$",
                "title": f"{self.breadcrumb_model} {self.breadcrumb_action}"
            }
        ]
        return url_patterns

    def get_breadcrumbs(self):
        breadcrumbs = []
        patterns = self.get_urls_patterns()
        path = self.request.path
        for pattern in patterns:
            match = re.search(pattern["pattern"], path)
            if match:
                breadcrumbs.append({
                    "title": pattern["title"],
                    "url": match.group()
                })
        return breadcrumbs
