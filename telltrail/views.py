"""
Views for telltrail.
"""
from django.http import HttpResponse, HttpResponseRedirect
from saaspire.utils import template, catch
from saaspire.telltrail.forms import *
from django.contrib import auth

@template('telltrail/landing.html')
def landing(request):
    """
    Landing page.
    """
    return {'location':'landing'}

@template('telltrail/signup.html')
def signup(request):
    """
    User sign up.
    """
    form = None
    if request.POST:
        form = SignupForm(request.POST)
        if form.is_valid():
            form.finish(request)
            return HttpResponseRedirect('/')
    else:
        form = SignupForm()
    return {'form':form}

def logout(request):
    """
    Logs the user out.
    """
    auth.logout(request)
    return HttpResponseRedirect('/')

@template('telltrail/login.html')
def login(request):
    """
    Logs the user in.
    """
    form = None
    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            form.login(request)
            return HttpResponseRedirect('/')
    else:
        form = LoginForm()
    return {'form':form,'location':'login'}

@template('telltrail/about.html')
def about(request):
    """
    About page.
    """
    return {'location':'about'}

# ===========
# = Control =
# ===========

@template('telltrail/control.html')
def control(request):
    """
    Control page.
    """
    return {'location':'control'}

@template('telltrail/control/info_edit.html')
def edit_personal_info(request):
    """
    Edits the user's personal info.
    """
    form = None
    if request.POST:
        form = PersonalInfoForm(request.POST)
        if form.is_valid():
            form.update_user(request.user)
            return 'OK'
    else:
        form = PersonalInfoForm()
        form.init(request.user)
    
    return {'form':form}

@template('telltrail/control/info_view.html')
def view_personal_info(request):
    """
    Views the personal info.
    """
    return {}

@template('telltrail/control/policy_edit.html')
def edit_policy(request):
    """
    Edits the main data policy.
    """
    form = None
    if request.POST:
        form = PolicyForm(request.POST)
        if form.is_valid():
            form.update_policy(request.user.get_profile().default_policy)
            return 'OK'
    else:
        form = PolicyForm()
        form.init(request.user.get_profile().default_policy)
    return {'form':form}

@template('telltrail/control/policy_view.html')
def view_policy(request):
    """
    Views the main policy.
    """
    return {}

@template('telltrail/control/identity_dialog.html')
def add_identity(request):
    """
    Adds a new identity.
    """
    form = None
    if request.POST:
        form = IdentityForm(request.POST)
        if form.is_valid():
            form.add_identity(request.user)
            return 'OK'
    else:
        form = IdentityForm()
    return {'form':form}

@template('telltrail/control/identity_list.html')
def list_identities(request):
    """
    Lists identities for the user.
    """
    return {}

@template('telltrail/control/identity_list.html')
def delete_identity(request,claim_id):
    """
    Deletes the user's claim on an identity.
    """
    try:
        claim = request.user.get_profile().identity_claims.get(pk=claim_id)
        claim.delete()
    except IdentityClaim.DoesNotExist:
        pass
    return {}

@template('telltrail/control/exception_dialog.html')
def add_exception(request):
    """
    Adds an exception.
    """
    form = None
    if request.POST:
        form = ExceptionForm(request.POST)
        if form.is_valid():
            form.add_exception(request.user)
            return 'OK'
    else:
        form = ExceptionForm()
    return {'form':form}

@template('telltrail/control/exception_list.html')
def list_exceptions(request):
    """
    Lists exceptions for the user.
    """
    return {}

@template('telltrail/control/exception_list.html')
def delete_exception(request,exception_id):
    """
    Deletes the policy exception.
    """
    try:
        policy_exception = request.user.get_profile().policy_exceptions.get(pk=exception_id)
        policy_exception.delete()
    except PolicyException.DoesNotExist:
        pass
    return {}

@template('telltrail/control/specific_policy_dialog.html')
def add_specific_policy(request):
    """
    Adds a new specific policy.
    """
    form = None
    if request.POST:
        form = SpecificPolicyForm(request.POST)
        if form.is_valid():
            form.add_specific(request.user)
            return 'OK'
    else:
        form = SpecificPolicyForm()
    return {'form':form}

@template('telltrail/control/policy_list.html')
def list_specific_policies(request):
    """
    Lists specific policies.
    """
    return {}

@template('telltrail/control/policy_list.html')
def delete_specific_policy(request,policy_id):
    """
    Deletes the specific policy.
    """
    try:
        policy = request.user.get_profile().specific_policies.get(pk=policy_id)
        policy.delete()
    except PolicyElement.DoesNotExist:
        pass
    return {}
