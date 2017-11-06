from django.conf.urls import url
from samples.views import SampleListView
from samples.views import SampleDetailView
from samples.views import SampleEditView

app_name = "samples"
urlpatterns = [
    url(r"^$", SampleListView.as_view(), name="sample_list"),
    url(r'^(?P<sample_id>[0-9]+)/$', SampleDetailView.as_view(),
        name='sample_details'),
    url(r'^(?P<sample_id>[0-9]+)/edit/$',
        SampleEditView.as_view(), name='sample_edit')
]
