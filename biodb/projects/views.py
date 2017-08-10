from django.shortcuts import render
from django.views.generic.list import ListView
from projects.models import Project
from projects.models import Tag
from django.core.exceptions import PermissionDenied
from biodb.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.generic import View, CreateView, DeleteView, UpdateView
# Create your views here.


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project


class TagsListView(LoginRequiredMixin, ListView):
    model = Tag

    def get(self, request, project_name, *args, **kwargs):
        """A base view for displaying a list of objects."""

        queryset = self.get_queryset()
        # self.object_list = Tag.objects.filter(project__name=project_name)
        self.object_list = queryset.filter(project__name=project_name)
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(self.object_list, 'exists'):
                is_empty = not self.object_list.exists()
            else:
                is_empty = len(self.object_list) == 0
            if is_empty:
                raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.") % {
                    'class_name': self.__class__.__name__,
                })
        context = self.get_context_data()
        return self.render_to_response(context)


class TagCreateView(CreateView):
    pass


class TagEditView(UpdateView):
    pass


class TagDeleteView(DeleteView):
    pass
