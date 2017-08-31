from django.conf.urls import url
from robjects.views import robjects_list_view
from robjects.views import SearchRobjectsView
from robjects.views import RobjectDetailView
from robjects.views import robjects_export_to_excel_view
from robjects.views import robjects_export_selected_to_excel_view

app_name="robjects"
urlpatterns = [
    url(r"^search/$",
        SearchRobjectsView.as_view(), name="search_robjects"),
    url(r"^$", robjects_list_view, name="robjects_list"),
    url(r'^(?P<pk>[0-9]+)/details/$',
        RobjectDetailView.as_view(), name='robject_details'),
    url(r'^(?P<pk>[0-9]+)/excel/$', robjects_export_to_excel_view, name='export_to_excel'),
    url(r'^excel/$', robjects_export_selected_to_excel_view, name='export_selected_to_excel')
]
