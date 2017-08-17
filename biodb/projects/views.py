from biodb.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
#from django.core.exceptions import DoesNotExist
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import View
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

    def get(self, request, project_name, *args, **kwargs):
        """A base view for displaying a list of objects."""
        # check if project exists
        try:
            project = Project.objects.get(name=project_name)
            # add project to view attributes
            self.project = project
        except Project.DoesNotExist:
            raise Http404
        return super(TagsListView, self).get(self, request, project_name, *args, **kwargs)

    def get_queryset(self):
        """
        Overwrite orginal qs and add filtering by project_name
        """
        # original queryset
        qs = super().get_queryset()

        # return filtered qs by project
        return qs.filter(project=self.project)


class TagCreateView(LoginRequiredMixin, CreateView):
    model = Tag
    fields = ['name']

    def get(self, request, project_name, *args, **kwargs):
        try:
            project = Project.objects.get(name=project_name)
        except Project.DoesNotExist:
            raise Http404

        return super(TagCreateView, self).get(self, request, project_name, *args, **kwargs)

    def form_valid(self, form):
        project_name = self.args[0]
        try:
            project = Project.objects.get(name=project_name)
            form.instance.project = project
        except Project.DoesNotExist:
            raise Http404
        return super(TagCreateView, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class TagEditView(UpdateView):
    model = Tag
    fields = ['name']
    template_name_suffix = '_update_form'


class TagDeleteView(LoginRequiredMixin, DeleteView):
    model = Tag
    #success_url = "/projects/%s/tags/" % (self.project.name)
