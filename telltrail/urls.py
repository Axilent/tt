from django.conf.urls import patterns, include, url

urlpatterns = patterns('telltrail.views',
    url(r'^$','landing'),
    url(r'^signup/$','signup'),
    url(r'^logout/$','logout'),
    url(r'^login/$','login'),
    url(r'^about/$','about'),
    url(r'^control/$','control'),
    url(r'^control/info/edit/$','edit_personal_info'),
    url(r'^control/info/$','view_personal_info'),
    url(r'^control/policy/edit/$','edit_policy'),
    url(r'^control/policy/$','view_policy'),
    url(r'^control/identity/add/$','add_identity'),
    url(r'^control/identity/list/$','list_identities'),
    url(r'^control/identity/(?P<claim_id>\d+)/delete/$','delete_identity'),
    url(r'^control/exception/add/$','add_exception'),
    url(r'^control/exception/list/$','list_exceptions'),
    url(r'^control/exception/(?P<exception_id>\d+)/delete/$','delete_exception'),
    url(r'^control/specific/add/$','add_specific_policy'),
    url(r'^control/specific/list/$','list_specific_policies'),
    url(r'^control/specific/(?P<policy_id>\d+)/delete/$','delete_specific_policy'),
)

# urlpatterns += patterns('',
#     (r'^api/',include('telltrail.api.urls')),
# )
#
# from django.conf import settings
#
# if settings.DEBUG:
#     urlpatterns += patterns('django.views.static',
#             (r'^static/(?P<path>.*)$','serve',{'document_root':settings.MEDIA_ROOT}),
#         )