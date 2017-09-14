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
# from projects.models import Tag
# Create your views here.


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
