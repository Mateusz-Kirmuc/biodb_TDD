from django.conf.urls import url
from samples.views import SampleListView
from samples.views import SampleDetailView
from django.http import HttpResponse
from samples.views import sample_create_view

app_name = "samples"
urlpatterns = [
    url(r"^$", SampleListView.as_view(), name="sample_list"),
    url(r'^(?P<sample_id>[0-9]+)/$', SampleDetailView.as_view(),
        name='sample_details'),
    url(r'^create/$', sample_create_view)
]
