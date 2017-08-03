from django.shortcuts import render
from biodb.mixins import LoginRequiredMixin
from django.views.generic import View
from robjects.models import Robject
from projects.models import Project
from django.core.exceptions import PermissionDenied

# Create your views here.


def robjects_list_view(request, project_name):
    if not request.user.is_authenticated():
        raise PermissionDenied
    project = Project.objects.get(name=project_name)
    robject_list = Robject.objects.filter(project=project)
    return render(request, "projects/robjects_list.html",
                  {"robject_list": robject_list, "project_name": project_name})


class SearchRobjectsView(LoginRequiredMixin, View):
    def get(self, request, project_name):
        query = request.GET.get("query")

        queryset = self.perform_search(query)

        return render(request, "projects/robjects_list.html",
                      {"robject_list": queryset, "project_name": project_name})

    def perform_search(self, query):
        """ Perform search for robjects using given query.
        """
        # search including name field
        name_qs = Robject.objects.filter(name__icontains=query)

        # search including author field
        author_qs = Robject.objects.filter(author__username=query)

        return name_qs | author_qs
