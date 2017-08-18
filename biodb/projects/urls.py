from django.conf.urls import url, include
from projects.views import ProjectListView
from projects.views import TagsListView
from projects.views import TagCreateView
from projects.views import TagEditView
from projects.views import TagDeleteView

app_name = 'projects'
urlpatterns = [
    url(r"^$", ProjectListView.as_view(), name="projects_list"),
    url(r"^(\w+)/robjects/", include("robjects.urls")),
    url(r"^(\w+)/tags/$", TagsListView.as_view(), name="tag_list"),
    url(r"^(\w+)/tags/create/$", TagCreateView.as_view(), name="tag_create"),
    url(r"^(\w+)/tags/(?P<pk>[0-9]+)/edit/$",
        TagEditView.as_view(), name="tag_edit"),
    url(r"^(\w+)/tags/(?P<pk>[0-9]+)/delete/$",
        TagDeleteView.as_view(), name="tag_delete"),
]
