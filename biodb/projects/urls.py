from django.conf.urls import url, include
from projects.views import ProjectListView

urlpatterns = [
    url(r"^$", ProjectListView.as_view(), name="projects_list"),
    url(r"^(?P<project_name>\w+)/robjects/", include("robjects.urls")),

]
