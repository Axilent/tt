"""
Container app for utility functions.
"""
from datetime import date
from django.db import models
from types import StringType, IntType, FloatType
from django.conf import settings
import traceback
import logging

log = logging.getLogger('telltrail')

def get_value(item,value_name):
    """
    Gets the specified value, first attempting to pull it as
    an attribute, and then as a dictionary key.
    """
    try:
        return getattr(item,value_name)
    except AttributeError:
        try:
            return item[value_name]
        except TypeError:
            raise AttributeError

def setting(key,default=None):
    """
    Gets a settings, using the default if the key is undefined.
    """
    if hasattr(settings,key) and getattr(settings,key):
        return getattr(settings,key)
    else:
        return default

def get_module(module_name):
    """
    Imports and returns the named module.
    """
    module = __import__(module_name)
    components = module_name.split('.')
    for comp in components[1:]:
        module = getattr(module,comp)
    return module

def backend(setting,default):
    """
    Loads the module specified in the setting name, or the specified default.
    """
    if hasattr(settings,setting) and getattr(settings,setting):
        return get_module(getattr(settings,setting))
    else:
        return get_module(default)

def get_function(module_name,function_name):
    """
    Imports and returns the named function in the specified module.
    """
    module = get_module(module_name)
    return getattr(module,function_name)

def gf(function_path):
    """
    Shortcut to get function.
    """
    module_name, function_name = function_path.rsplit('.',1)
    return get_function(module_name,function_name)

def get_object(module_name,class_name,id):
    """
    Gets the identified object.
    """
    clazz = get_function(module_name,class_name)
    return clazz.objects.get(pk=id)

import hashlib
import random
import sys

def random_hex():
    """
    Returns a random hex string.
    """
    return hashlib.sha256(str(random.randint(0,sys.maxint - 1)) + str(random.randint(0, sys.maxint - 1)) + settings.SECRET_KEY).hexdigest()

# ===============================
# = Decorator to simplify views =
# ===============================
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse

def template(template_name):
    """
    Parameterized decorator to allow a view to return a context dictionary as a response.
    The decorator will place the dictionary in a RequestContext wrapper, and return using
    the template specified in the parameter.
    """
    from telltrail.models import CanonicalIdentity
    def function_builder(func):
        def view(request,*args,**kwargs):
            response = func(request,*args,**kwargs)
            if isinstance(response,HttpResponse):
                return response
            elif response == 'OK':
                return HttpResponse('OK')
            else:
                ctx = RequestContext(request)
                if not request.user.is_anonymous() and CanonicalIdentity.objects.filter(user=request.user).exists():
                    ctx['ci'] = CanonicalIdentity.objects.get(user=request.user)
                return render_to_response(template_name,response,context_instance=ctx)
        return view
    return function_builder

# ============================================
# = Dynamic population of Form choice fields =
# ============================================
class DynamicFormMixin(object):
    """
    Augments form classes to increase convenience of dynamically populated choice fields.
    """
    def init_choices(self,choice_dict):
        """
        Initializes choice fields with values in the dictionary.  The dictionary should
        use the names of choice fields as keys, and a list of choices for those fieldds 
        as values.
        """
        for field_name, choices in choice_dict.items():
            self.fields[field_name].choices = choices

catch_logger = logging.Logger('telltrail')

def catch(func):
    """
    Catches any exception and prints a stack trace.
    """
    def wrapper(*args,**kwargs):
        try:
            return func(*args,**kwargs)
        except:
            log.exception('Exception while executing function %s' % str(func))
            traceback.print_exc()

    return wrapper
