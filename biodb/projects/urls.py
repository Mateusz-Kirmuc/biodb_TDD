from django.conf.urls import url
from django.conf.urls import include
from projects.views import ProjectListView
# from projects.views import TagsListView
# from projects.views import TagCreateView
# from projects.views import TagEditView
# from projects.views import TagDeleteView
# from samples.views import SampleListView
# app_name = 'projects'

urlpatterns = [
    url(r"^$", ProjectListView.as_view(), name="projects_list"),
    url(r"^(?P<project_name>\w+)/robjects/", include("robjects.urls")),
]
