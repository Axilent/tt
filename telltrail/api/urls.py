from piston.resource import Resource
from telltrail.api.handlers import *
from django.conf.urls import *
from django.conf.urls.defaults import *

policy_handler = Resource(PolicyHandler)

urlpatterns = patterns('',
    url(r'^(?P<api_key>[a-f0-9]+)/policy/$',policy_handler),
)