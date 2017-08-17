from django.conf.urls import url, include
from projects.views import ProjectListView, TagsListView, TagCreateView, TagEditView, TagDeleteView

urlpatterns = [
    url(r"^$", ProjectListView.as_view(), name="projects_list"),
    url(r"^(\w+)/robjects/", include("robjects.urls")),
    url(r"^(\w+)/tags/$", TagsListView.as_view(), name="tag_list"),
    url(r"^(\w+)/tags/create/$", TagCreateView.as_view(), name="tag_form"),
    url(r"^(\w+)/tags/(?P<pk>[0-9]+)/edit/$", TagEditView.as_view(), name="tag_edit"),
    url(r"^(\w+)/tags/(?P<pk>[0-9]+)/delete/$", TagDeleteView.as_view(), name="tag_delete"),
    ]
