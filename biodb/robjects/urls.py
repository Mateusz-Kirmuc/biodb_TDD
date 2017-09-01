from django.conf.urls import url
from robjects.views import ExportExcelView
from robjects.views import ExportPdfView
from robjects.views import RobjectDetailView
from robjects.views import robjects_list_view
from robjects.views import SearchRobjectsView

app_name="robjects"
urlpatterns = [
    url(r'^search/$',
        SearchRobjectsView.as_view(), name="search_robjects"),
    url(r'^$', robjects_list_view, name="robjects_list"),
    url(r'^(?P<pk>[0-9]+)/details/$',
        RobjectDetailView.as_view(), name='robject_details'),
    url(r'^raport_pdf/$', ExportPdfView.as_view(), name='raport_pdf'),
    url(r'^excel/$', ExportExcelView.as_view(), name='export_to_excel'),
]
