from django.conf.urls import url
from django.contrib.auth.views import (password_reset, password_reset_done, password_reset_confirm,
                                       password_reset_complete)
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'DMS'

urlpatterns = [
    url(r'^index/$', views.index, name='index'),
    url(r'^(?P<pk>[0-9]+)/$', views.FolderDetail, name='folder-details'),
    url(r'^(?P<folder_id>[0-9]+)/create_document/$', views.create_document, name='create_document'),
    url(r'^create_folder/$', views.create_folder, name='create-folder'),
    url(r'^login/$', views.user_login, name='user_login'),
    url(r'^logout/$', views.user_logout, name='user_logout'),
    url(r'^doc/$', views.DocumentView, name='document'),
    url(r'^(?P<pk>[0-9]+)/versions/(?P<document_id>[0-9]+)/$', views.versions, name='versions'),
    url(r'^(?P<folder_id>[0-9]+)/delete_document/(?P<document_id>[0-9]+)/$', views.delete_document,
        name='delete_document'),
    url(r'^(?P<folder_id>[0-9]+)/check_in/(?P<document_id>[0-9]+)/$', views.checkin_document,
        name='checkin_document'),
    url(r'^(?P<id_folder>[0-9]+)/delete_folder/$', views.delete_folder, name='delete_folder'),

    url(r'^reset-password/$', password_reset,
        {'template_name': 'registration/password_reset_form.html', 'post_reset_redirect': 'DMS:password_reset_done',
         'email_template_name': 'registration/password_reset_email.html'}, name='reset_password'),

    url(r'^reset-password/done/$', password_reset_done, {'template_name': 'registration/password_reset_done.html'},
        name='password_reset_done'),

    url(r'^reset-password/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm,
        {'template_name': 'registration/password_reset_confirm.html',
         'post_reset_redirect': 'DMS:password_reset_complete'}, name='password_reset_confirm'),

    url(r'^reset-password/complete/$', password_reset_complete,
        {'template_name': 'registration/password_reset_complete.html'}, name='password_reset_complete'),
    url(r'^test_view/(?P<pk>\d+)$', views.DocumentHistoryCompareView.as_view() ),
    # url(r'^document/add/$', views.DocumentCreate.as_view(), name='document-add'),
    # url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    # url(r'^?q=/', views.FolderDetail, name='folder-details'),

    # url(r'^folder/add/$', views.FolderCreate.as_view(), name='folder-add'),


]

urlpatterns = format_suffix_patterns(urlpatterns)

