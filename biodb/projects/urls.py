from django.conf.urls import url, include
from projects.views import ProjectListView
from projects.views import TagsListView
app_name = 'projects'
urlpatterns = [
    url(r"^$", ProjectListView.as_view(), name="projects_list"),
    url(r"^(?P<project_name>\w+)/tags/$", TagsListView.as_view(), name="tag_list"),
    url(r"^(?P<project_name>\w+)/robjects/", include("robjects.urls"))
]
