"""Views for robject search."""
from biodb.mixins import LoginPermissionRequiredMixin

from django_tables2 import SingleTableView

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django.views.generic.list import ListView

from projects.models import Project
from samples.models import Sample
from samples.tables import SampleTable


class SampleListView(LoginPermissionRequiredMixin, SingleTableView, ListView):
    model = Sample
    template_name = "samples/samples_list.html"
    table_class = SampleTable
    permissions_required = ["can_visit_project"]

    def dispatch(self, request, *args, **kwargs):
        if 'project_name' in self.kwargs:
            project = get_object_or_404(Project,
                                        name=self.kwargs['project_name'])
            self.project = project
        else:
            raise Http404
        request.session['_succes_url'] = self.request.build_absolute_uri()
        return super(SampleListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Overwrite orginal qs and add filtering by robject
        """
        # original queryset
        qs = super(SampleListView, self).get_queryset()
        qs = qs.filter(robject__project=self.project)
        return qs

    def get_context_data(self, **kwargs):
        context = super(SampleListView, self).get_context_data(**kwargs)
        context['project'] = self.project
        return context


class SampleDetailView(LoginPermissionRequiredMixin, DetailView):
    model = Sample
    template_name = 'samples/sample_details.html'
    pk_url_kwarg = "sample_id"
    permissions_required = ["can_visit_project"]
