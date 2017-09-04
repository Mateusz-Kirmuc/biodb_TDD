"""Views for robject search."""
import re
from django.contrib.auth.decorators import login_required
from bs4 import BeautifulSoup
from datetime import datetime
from django.core.exceptions import PermissionDenied
from django.db.models import CharField
from biodb.mixins import LoginRequiredMixin
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import ForeignKey
from django.db.models import TextField
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import View
from openpyxl import Workbook
from projects.mixin import ExportViewMixin
from projects.models import Project
from robjects.models import Robject
from robjects.models import Tag
from weasyprint import CSS
from weasyprint import HTML


def robjects_list_view(request, project_name):
    if not request.user.is_authenticated():
        raise PermissionDenied
    project = Project.objects.get(name=project_name)
    robject_list = Robject.objects.filter(project=project)
    return render(request, "projects/robjects_list.html",
                  {"robject_list": robject_list, "project_name": project_name})


def robjects_selected_pdf_view(request, *args, **kwargs):
    '''Gets list of robjects ids, POSTed by checkboxes in request.
        View renders the same template and css as robjects_pdf_view.
    '''
    robject_list = []
    if "checkbox" in request.POST:
        pk_list = request.POST.getlist("checkbox")

    else:
        pk_list = []
    # create template from file
    html_template = get_template('robjects/robject_raport_pdf.html')
    # get robjects from pk_list
    robjects = Robject.objects.filter(pk__in=pk_list)
    for el in pk_list:
        pk = el

    rendered_html = html_template.render(
        {'pk': pk, 'robjects': robjects}).encode(encoding="UTF-8")
    # # generate pdf from rendered html
    pdf_file = HTML(string=rendered_html).write_pdf(
        stylesheets=[CSS(settings.BASE_DIR + '/robjects' +
                         settings.STATIC_URL + 'robjects/css/raport_pdf.css')],
    )
    # Add file object to response
    http_response = HttpResponse(pdf_file, content_type='application/pdf')
    http_response['Content-Disposition'] = 'filename="robject_raport.pdf"'
    # return response
    return http_response


class ExportExcelView(ExportViewMixin, View):
    model = Robject
    queryset = None

    def get_queryset(self, project_name):
        """
        Return the list of items for this view.
        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
        if self.queryset is not None:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                queryset = queryset.filter(project__name=project_name).all()
        elif self.model is not None:
            queryset = self.model._default_manager.filter(
                project__name=project_name).all()  # ???
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {
                    'cls': self.__class__.__name__
                }
            )
        if self.request.GET and self.request.GET.getlist('checkbox'):
            queryset = queryset.filter(
                pk__in=self.request.GET.getlist('checkbox'))

        return queryset

    def get(self, request, project_name, *args, **kwargs):

        self.object_list = self.get_queryset(project_name)
        if not self.object_list:
            raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.") % {
                'class_name': self.__class__.__name__,
            })
        return self.export_to_excel(self.object_list)


class ExportPdfView(ExportViewMixin, View):
    model = Robject
    pdf_template_name = "robjects/robject_raport_pdf.html"
    pdf_css_name = 'robjects/css/raport_pdf.css'
    css_sufix = '/robjects'

    def get(self, request, project_name, *args, **kwargs):

        self.object_list = self.get_queryset(project_name)
        if not self.object_list:
            raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.") % {
                'class_name': self.__class__.__name__,
            })
        return self.export_to_pdf(self.object_list)


class ExportPdfTableView(ExportViewMixin, View):
    model = Robject
    pdf_template_name = "robjects/raport_table_pdf.html"
    pdf_css_name = 'robjects/css/raport_table_pdf.css'
    css_sufix = '/robjects'

    def get(self, request, project_name, *args, **kwargs):

        self.object_list = self.get_queryset(project_name)
        if not self.object_list:
            raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.") % {
                'class_name': self.__class__.__name__,
            })
        return self.export_to_pdf(self.object_list)


class SearchRobjectsView(LoginRequiredMixin, View):
    # TODO: Add multipleObjectMixin to inherit by this class??
    model = Robject

    def get(self, request, project_name):
        query = request.GET.get("query")

        queryset = self.perform_search(query, project_name)

        return render(request, "projects/robjects_list.html",
                      {"robject_list": queryset, "project_name": project_name})

    def normalize_query(self, query_string,
                        findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                        normspace=re.compile(r'\s{2,}').sub):
        """Splits the query string in invidual keywords, getting rid of
           unecessary spaces and grouping quoted words together.

            Args:
                query_string (str): string with query words

            Example:
                >>> normalize_query('some random  words "with   quotes  "
                                    and   spaces  ')
                ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

            Returns:
                the list of words
        """
        terms = [normspace(
            ' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]
        return terms

    def perform_search(self, query, project_name):
        """Perform search for robjects using given query.

        Normalize search string and divede them into search terms.
        Create list of search queris for CharField and TextField.

        Args:
            query (str): Search string provieded by user
            project_name (str): name of the project (auto).

        Returns:
            model objects list (list): filtered list of model objects
            model is filtered based on Q objects Complex SQL expression
            in Django (see Django docs) and project_name
        """
        # normalize query string and get the list of words (search terms)
        terms = self.normalize_query(query)
        # get list of text fields
        text_fields = [f for f in self.model._meta.get_fields() if isinstance(
            f, (CharField, TextField))]
        # get the list of foreig fields
        foreign_fields = [
            f for f in self.model._meta.get_fields()
            if isinstance(f, ForeignKey)]
        # get dict with ForeigKey field as key and list of Char/Text fields
        # that are in related model as a argument
        foreign_models_fields = {}
        for foreign_field in foreign_fields:
            fmodel = self.model._meta.get_field(
                '%s' % foreign_field.name).rel.to
            foreign_models_fields[foreign_field] = [
                f for f in fmodel._meta.fields
                if isinstance(f, (CharField, TextField))]

        # define Q() objects to use or on queries
        qs = Q()
        # iterate over all search terms and create the queries
        # for model text fields and foreign text fields
        for term in terms:
            # get queries for Char/Text fields
            queries = [Q(**{'%s__icontains' % f.name: term})
                       for f in text_fields]
            # exted queries by foreign fields
            if foreign_models_fields:
                for foreign_field, model_fields \
                        in foreign_models_fields.items():
                    queries += [Q(**{'%s__%s__icontains' %
                                     (foreign_field.name, f.name): term})
                                for f in model_fields]
            # perform logical OR on queries
            if queries:
                for qs_query in queries:
                    qs = qs | qs_query

        # project reqired
        return self.model.objects.filter(qs, project__name=project_name)


class RobjectDetailView(DetailView):
    model = Robject
