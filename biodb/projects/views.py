from biodb.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
# from django.core.exceptions import DoesNotExist
# from django.core.exceptions import PermissionDenied
# from django.core.exceptions import ValidationError
from django.http import Http404
# from django.http import HttpResponse
# from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
# from django.views.generic import View
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import UpdateView
from django.views.generic.list import ListView
from projects.models import Project
from projects.models import Tag
# Create your views here.


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project


class TagsListView(LoginRequiredMixin, ListView):
    model = Tag
    template_name = "tags/tag_list.html"

    # @method_decorator(login_required)

    def dispatch(self, request, project_name, *args, **kwargs):
        print(self.kwargs)
        return super(TagsListView, self).dispatch(request, *args, **kwargs)


    def get(self, request, *args, **kwargs):
        """A base view for displaying a list of objects."""
        # check if project exists
        try:
            project = Project.objects.get(name=self.kwargs['project_name'])
            # add project to view attributes
            self.project = project
        except Project.DoesNotExist:
            raise Http404
        return super(TagsListView, self).get(request, *args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        """
        Overwrite orginal qs and add filtering by project_name
        """
        # print(args)
        # original queryset
        # print(*kwargs)
        qs = super().get_queryset(*kwargs)
        # return filtered qs by project
        return qs.filter(project=self.project)

    def get_context_data(self, **kwargs):
        context = super(TagsListView, self).get_context_data(**kwargs)
        context['project'] = self.project
        return context
