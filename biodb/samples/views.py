"""Views for robject search."""
from biodb.mixins import LoginPermissionRequiredMixin

from django_tables2 import SingleTableView

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.core.urlresolvers import reverse
from projects.models import Project
from samples.models import Sample
from samples.tables import SampleTable
from robjects.models import Robject
from django.contrib.auth.models import User
from django.db.utils import IntegrityError


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

    def get_permission_object(self):
        project = self.project
        return project

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

    def get_permission_object(self):
        project = get_object_or_404(Project, name=self.kwargs['project_name'])
        return project


def sample_create_view(request, project_name, robject_id):
    owner_options = [user.username for user in User.objects.all(
    ) if user.username != "AnonymousUser"]

    if request.user.is_anonymous == True:
        redirect_to = f"{reverse('login')}?next={request.path}"
        return redirect(redirect_to)
    if request.method == "POST":
        code = request.POST.get("code", "")
        if not code:
            return render(request, "samples/sample_create.html", {
                "owners": owner_options,
                "error": "This field is required",
                "notes_value": request.POST.get("notes"),
                "form_value": request.POST.get("form"),
                "source_value": request.POST.get("source"),
                "selected_owner": request.POST.get("owner")
            })

        try:
            s = Sample.objects.create(
                code=code,
                robject=Robject.objects.get(id=robject_id),
                owner=User.objects.get(username=request.POST.get("owner")),
                status=request.POST.get("status")
            )
        except IntegrityError:
            return render(request, "samples/sample_create.html", {
                "owners": owner_options,
                "error": "Sample code must be uniqe"
            })
        if request.user.is_authenticated:
            s.modify_by = request.user
            s.save()

        redirect_to = reverse(
            "projects:samples:sample_details",
            kwargs={"project_name": project_name, "sample_id": s.id})

        return redirect(redirect_to)

    permission_against = Project.objects.get(name=project_name)

    if not request.user.has_perm("projects.can_visit_project", permission_against):
        return render(request, template_name="biodb/visit_permission_error.html")
    if not request.user.has_perm("projects.can_modify_project", permission_against):
        return render(request, "biodb/modify_permission_error.html")

    return render(request, "samples/sample_create.html", {"owners": owner_options})
