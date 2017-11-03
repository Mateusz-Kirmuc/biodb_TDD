from django.conf.urls import url
from robjects.views import robjects_list_view, SearchRobjectsView
from django.http import HttpResponse
from robjects.views import RobjectCreateView, NameCreateView, TagCreateView, RobjectDeleteView
from robjects.views import RobjectHistoryView
from robjects.views import RobjectSamplesList
from robjects.views import RobjectEditView
from robjects.views import ExportExcelView
from robjects.views import RobjectPDFeView
from robjects.views import RobjectListView

app_name = 'robjects'
urlpatterns = [
    url(r"^$", RobjectListView.as_view(), name="robjects_list"),
    url(r"^search/$",
        SearchRobjectsView.as_view(), name="search_robjects"),
    url(r"^create/$", RobjectCreateView.as_view(), name="robject_create"),
    url(r"^delete/$", RobjectDeleteView.as_view(), name="robject_delete"),
    url(r"^excel/$", ExportExcelView.as_view(), name="raport_excel"),
    url(r"^pdf/$", RobjectPDFeView.as_view(), name="pdf_raport"),
    url(r"^names-create/$", NameCreateView.as_view(), name="names_create"),
    url(r"^tags-create/$", TagCreateView.as_view(), name="tags_create"),
    url(r'^(?P<robject_id>[0-9]+)/samples/$',
        RobjectSamplesList.as_view(), name='robject_samples'),
    url(r"^(?P<robject_id>\d+)/history/$", RobjectHistoryView.as_view(),
        name="robject_history"),
    url(r'^(?P<robject_id>[0-9]+)/edit/$',
        RobjectEditView.as_view(), name="robject_edit")
]
