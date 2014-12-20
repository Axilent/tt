from django.conf.urls.defaults import *

urlpatterns = patterns('saaspire.telltrail.views',
    (r'^$','landing'),
    (r'^signup/$','signup'),
    (r'^logout/$','logout'),
    (r'^login/$','login'),
    (r'^about/$','about'),
    (r'^control/$','control'),
    (r'^control/info/edit/$','edit_personal_info'),
    (r'^control/info/$','view_personal_info'),
    (r'^control/policy/edit/$','edit_policy'),
    (r'^control/policy/$','view_policy'),
    (r'^control/identity/add/$','add_identity'),
    (r'^control/identity/list/$','list_identities'),
    (r'^control/identity/(?P<claim_id>\d+)/delete/$','delete_identity'),
    (r'^control/exception/add/$','add_exception'),
    (r'^control/exception/list/$','list_exceptions'),
    (r'^control/exception/(?P<exception_id>\d+)/delete/$','delete_exception'),
    (r'^control/specific/add/$','add_specific_policy'),
    (r'^control/specific/list/$','list_specific_policies'),
    (r'^control/specific/(?P<policy_id>\d+)/delete/$','delete_specific_policy'),
)

urlpatterns += patterns('',
    (r'^api/',include('saaspire.telltrail.api.urls')),
)

from django.conf import settings

if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
            (r'^static/(?P<path>.*)$','serve',{'document_root':settings.MEDIA_ROOT}),
        )