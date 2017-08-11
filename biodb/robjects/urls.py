from django.conf.urls import url
from robjects.views import CreateRobjectView
from robjects.views import CreateNameView
from robjects.views import SearchRobjectsView
from robjects.views import robjects_list_view, SearchRobjectsView

urlpatterns = [
    url(r"^search/$",
        SearchRobjectsView.as_view(), name="search_robjects"),
    url(r"^$", robjects_list_view, name="robjects_list"),
    url(r"^create/", CreateRobjectView.as_view(), name="add_robject"),
    url(r"^name-create/", CreateNameView.as_view(), name="add_name"),
]
