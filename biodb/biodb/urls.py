from django.conf.urls import include, url
from django.contrib import admin
from biodb import views
from django.http import HttpResponse
from django.shortcuts import render
from projects.views import ProjectListView

app_name = "biodb"
urlpatterns = [
    # Examples:
    # url(r'^$', 'biodb.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.RedirectView.as_view(), name="welcome_page"),
    url(r'^projects/', include("projects.urls"), name="projects_list"),
    url(r'^accounts/', include("accounts.urls")),
    url(r'^admin/', include(admin.site.urls)),
]
