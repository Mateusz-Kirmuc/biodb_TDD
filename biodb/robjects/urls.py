from django.conf.urls import url
from robjects.views import robjects_list_view, SearchRobjectsView
from django.http import HttpResponse
from robjects.views import RobjectCreateView, NameCreateView, TagCreateView, RobjectDeleteView
from robjects.views import RobjectSamplesList
from robjects.views import RobjectEditView
from robjects.views import ExportExcelView

app_name = 'robjects'
urlpatterns = [
    url(r"^search/$",
        SearchRobjectsView.as_view(), name="search_robjects"),
    url(r"^$", robjects_list_view, name="robjects_list"),
    url(r"^create/$", RobjectCreateView.as_view(), name="robject_create"),
    url(r"^delete/$", RobjectDeleteView.as_view(), name="robject_delete"),
    url(r"^excel-raport/$", ExportExcelView.as_view(), name="raport_Excel"),
    url(r"^names-create/$", NameCreateView.as_view(), name="names_create"),
    url(r"^tags-create/$", TagCreateView.as_view(), name="tags_create"),
    url(r'^(?P<robject_id>[0-9]+)/samples/$',
        RobjectSamplesList.as_view(), name='robject_samples'),
    url(r'^(?P<robject_id>[0-9]+)/edit/$',
        RobjectEditView.as_view(), name="robject_edit")
]
