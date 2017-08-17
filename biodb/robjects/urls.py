from django.conf.urls import url
from robjects.views import robjects_list_view, SearchRobjectsView, RobjectDetailView

app_name="robjects"
urlpatterns = [
    url(r"^search/$",
        SearchRobjectsView.as_view(), name="search_robjects"),
    url(r"^$", robjects_list_view, name="robjects_list"),
    url(r'^(?P<pk>[0-9]+)/details/$',
        RobjectDetailView.as_view(), name='robject_details'),
]
