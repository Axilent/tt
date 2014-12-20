"""
Container app for utility functions.
"""
from datetime import date
from django.db import models
from types import StringType, IntType, FloatType
from django.conf import settings
import traceback
import logging

log = logging.getLogger('saaspire.utils')

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

def breadth_first(tree,children=iter):
    """
    Traverse the nodes of a tree in breadth-first order.
    The first argument should be the tree root; children
    should be a function taking as argument a tree node and
    returning an iterator of the node's children.

    -- ActiveState Recipe 231503: Breadth first traversal of tree
    """
    yield tree
    last = tree
    for node in breadth_first(tree,children):
        for child in children(node):
            yield child
            last = child
        if last == node:
            return

from django.contrib.contenttypes.models import ContentType

def get_model(model_key):
    """
    Retrieves content by the specified compound content key.

    The key should follow the format:

    <app_label>:<model>:<primary_key>

    So for example, getting a User with an id of 4 would be:

    auth:user:4
    """
    
    if isinstance(model_key,models.Model):
        return model_key
    
    app_label, model_name, pk_string = model_key.split(':')
    pk = int(pk_string)
    content_type = ContentType.objects.get(app_label=app_label,model=model_name)
    return content_type.model_class().objects.get(pk=pk)

def get_model_key(model):
    """
    Gets the model key for the model
    """
    if isinstance(model,StringType):
        return model # assume model key passed in unnecessarily

    content_type = ContentType.objects.get_for_model(model)
    return '%s:%s:%d' % (content_type.app_label,content_type.model,model.pk)

content_model_dict = {}
model_content_dict = {}

def is_model_key(key):
    """
    Returns boolean value indicating if the specified key is a model key.
    """
    if not key:
        return False # get rid of the nulls

    if not isinstance(key,StringType):
        return False # get rid of non-strings

    try:
        label,model,pk = key.split(':')
        pk_int = int(pk)
        return True
    except ValueError:
        # either didn't split okay or pk isn't an integer
        return False

def content_key_to_model_key(content_key):
    """
    Gets the content key for the specified model key.
    """
    content_name, pk_string = content_key.split(':')
    app_label, model_name = None, None
    try:
        app_label, model_name = content_model_dict[content_name]
        return '%s:%s:%s' % (app_label,model_name,pk_string)
    except KeyError:
        content_type = UserContentType.objects.get(name=content_name)
        content_model_dict[content_name] = (content_type.app_label,content_type.model_name)
        return '%s:%s:%s' % (content_type.app_label,content_type.model_name,pk_string)

def model_key_to_content_key(model_key):
    """
    Gets the content key for the specified model key.
    """
    from saaspire.content.models import Content
    app_label, model_name, pk_string = model_key.split(':')
    try:
        content = Content.objects.get(pk=int(pk_string))
        model_content_dict[(app_label,model_name)] = content.user_content_type.name
        return '%s:%s' % (content.user_content_type.name,pk_string)
    except Content.DoesNotExist:
        raise ValueError, '%s is not a valid content key.' % model_key

def get_content_from_request(request,scope,variable):
    """
    Gets content from the incoming request, based on a content key
    in the specified scope, under the specified variable name.
    """
    return get_content(getattr(request,scope)[variable])

def get_content_type(content_key):
    """
    Gets content type based on specified content key.  A content
    key is defined in the form of:

    <app_label>:<model>

    so a user from django.contrib.auth would be

    auth:user
    """
    app_label, model_name = content_key.split(':')
    return ContentType.objects.get(app_label=app_label,model=model_name)

def from_datestring(datestring):
    """
    Creates a date object from a string.  String must be in YYYY-MM-DD format.
    """
    year, month, day = [int(string) for string in datestring.split('-')]
    return date(year,month,day)

def is_datestring(datestring):
    """
    Determines if the string is a date format string.
    """
    try:
        year, month, day = [int(string) for string in datestring.split('-')]
        d = date(year,month,day)
        return True
    except ValueError:
        return False

def get_datatype(instance):
    """
    Gets the datatype for the instance.
    """
    if isinstance(instance,IntType):
        return 'integer'
    elif isinstance(instance,FloatType):
        return 'float'
    elif is_model_key(instance):
        return 'pointer'
    elif is_datestring(instance):
        return 'date'
    elif isinstance(instance,StringType):
        return 'string'
    else:
        raise ValueError, 'Unknown datatype: %s' % str(instance)

def kwargs_safe(dictionary):
    """
    Converts keys for dictionary to string objects, making it safe
    to unpack them into a '**kwargs' argument.
    """
    kwargs = {}
    for key, value in dictionary.items():
        kwargs[str(key)] = value
    return kwargs

import hashlib
import random
import sys

def random_hex():
    """
    Returns a random hex string.
    """
    return hashlib.sha256(str(random.randint(0,sys.maxint - 1)) + str(random.randint(0, sys.maxint - 1)) + settings.SECRET_KEY).hexdigest()

class PyrohoseModel(object):
    """
    Mixin to provide model key functionality.
    """
    @property
    def mk(self):
        """
        Model key.
        """
        return get_model_key(self)
    
    @classmethod
    def get_model(clazz,model_key):
        """
        Gets this model by the specified model key.
        """
        if model_key.__class__ == clazz:
            return model_key # this is already the model
        
        pk = int(model_key.split(':')[-1])
        return clazz.objects.get(pk=pk)

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
    def function_builder(func):
        def view(request,*args,**kwargs):
            response = func(request,*args,**kwargs)
            if isinstance(response,HttpResponse):
                return response
            elif response == 'OK':
                return HttpResponse('OK')
            else:
                return render_to_response(template_name,response,context_instance=RequestContext(request))
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

catch_logger = logging.Logger('exception catcher')

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
