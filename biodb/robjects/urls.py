from django.conf.urls import url

from robjects.views import NameCreateView
from robjects.views import ExportExcelView
from robjects.views import RobjectCreateView
from robjects.views import RobjectDeleteView
from robjects.views import RobjectEditView
from robjects.views import RobjectHistoryView
from robjects.views import RobjectListView
from robjects.views import RobjectPDFeView
from robjects.views import RobjectSamplesList
from robjects.views import SearchRobjectsView
from robjects.views import TagCreateView
from django.http import HttpResponse

app_name = 'robjects'
urlpatterns = [
    url(r"^search/$",
        SearchRobjectsView.as_view(), name="search_robjects"),
    url(r"^$", RobjectListView.as_view(), name="robjects_list"),
    url(r"^create/$", RobjectCreateView.as_view(), name="robject_create"),
    url(r'^(?P<robject_id>[0-9]+)/edit/$',
        RobjectEditView.as_view(), name="robject_edit"),
    url(r"^delete/$", RobjectDeleteView.as_view(), name="robject_delete"),
    url(r"^excel-raport/$", ExportExcelView.as_view(), name="raport_excel"),
    url(r"^(?P<robject_id>\d+)/history/$", RobjectHistoryView.as_view(),
        name="robject_history"),
    url(r"^PDF-raport/$", RobjectPDFeView.as_view(), name="pdf_raport"),
    url(r"^names-create/$", NameCreateView.as_view(), name="names_create"),
    url(r"^tags-create/$", TagCreateView.as_view(), name="tags_create"),
    url(r'^(?P<robject_id>[0-9]+)/samples/$',
        RobjectSamplesList.as_view(), name='robject_samples'),
    url(r'^(?P<robject_id>[0-9]+)/details/',
        lambda request, project_name, robject_id: HttpResponse(
            f"<a href='/projects/{project_name}/robjects/{robject_id}/samples/create/'>Create sample</a>"
        ))
]
