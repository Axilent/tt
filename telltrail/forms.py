"""
Forms for TellTrail.
"""
from django import forms
from django.contrib.auth.models import User
from django.contrib import auth
from telltrail.models import *
import re

class SignupForm(forms.Form):
    """
    Primary form for sign-up.
    """
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    city = forms.CharField(required=False,help_text='Optional')
    zip_code = forms.CharField(required=False,help_text='Optional')
    
    def clean_username(self):
        """
        Cleans the username field.
        """
        if self.cleaned_data.get('username',None):
            try:
                User.objects.get(username=self.cleaned_data['username'])
                raise forms.ValidationError('A user with that user name already exists.')
            except User.DoesNotExist:
                pass
        
        return self.cleaned_data['username']
    
    def clean_zip_code(self):
        """
        Cleaner for zip code.
        """
        zc = self.cleaned_data.get('zip_code',None)
        if zc:
            if len(zc) == 10:
                if re.match('^[0-9]{5}-[0-9]{4}$',zc):
                    return zc
            elif len(zc) == 5:
                if re.match('^[0-9]{5}$',zc):
                    return zc
            
            # If we're here it's a bad zip code
            raise forms.ValidationError('Please use a properly formatted zip code. Example: 11201-1044 or 11201.')
        else:
            return zc
    
    def clean(self):
        """
        Password and password confirm must match.
        """
        if self.cleaned_data.get('password',None) and self.cleaned_data.get('confirm_password',None):
            if self.cleaned_data['password'] != self.cleaned_data['confirm_password']:
                raise forms.ValidationError('Passwords must match.')
        return self.cleaned_data
    
    def finish(self,request):
        """
        Finishes the creation of the user, the CanonicalIdentity and authenticates the user.
        """
        user = User.objects.create(username=self.cleaned_data['username'],
                                   first_name=self.cleaned_data['first_name'],
                                   last_name=self.cleaned_data['last_name'],
                                   email=self.cleaned_data['email'])
        
        user.set_password(self.cleaned_data['password'])
        user.save()
        can_id = CanonicalIdentity.objects.create(user=user)
        
        # Optional location data
        if self.cleaned_data.get('city',None):
            can_id.city = self.cleaned_data['city']
        if self.cleaned_data.get('zip_code',None):
            can_id.zip_code = self.cleaned_data['zip_code']
        can_id.save()
        
        retrieved_user = auth.authenticate(username=self.cleaned_data['username'],password=self.cleaned_data['password'])
        auth.login(request,retrieved_user)

class LoginForm(forms.Form):
    """
    Login form.
    """
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    
    def clean(self):
        """
        Cleaner.
        """
        if self.cleaned_data.get('username',None) and self.cleaned_data.get('password',None):
            user = auth.authenticate(username=self.cleaned_data['username'],password=self.cleaned_data['password'])
            if user:
                return self.cleaned_data
        
        raise forms.ValidationError('Sorry we can\'t log you in with that username or password.')
    
    def login(self,request):
        """
        Logs in the user.
        """
        user = auth.authenticate(username=self.cleaned_data['username'],password=self.cleaned_data['password'])
        auth.login(request,user)
    

class PersonalInfoForm(forms.Form):
    """
    Personal information update form.
    """
    first_name = forms.CharField()
    last_name = forms.CharField()
    city = forms.CharField(required=False,help_text='Optional')
    zip_code = forms.CharField(required=False,help_text='Optional')
    
    def clean_zip_code(self):
        """
        Cleaner for zip code.
        """
        zc = self.cleaned_data.get('zip_code',None)
        if zc:
            if len(zc) == 10:
                if re.match('^[0-9]{5}-[0-9]{4}$',zc):
                    return zc
            elif len(zc) == 5:
                if re.match('^[0-9]{5}$',zc):
                    return zc
            
            # If we're here it's a bad zip code
            raise forms.ValidationError('Please use a properly formatted zip code. Example: 11201-1044 or 11201.')
        else:
            return zc
    
    def init(self,user):
        """
        Initializes the form with the user data.
        """
        ci = CanonicalIdentity.objects.get(user=user)
        self.initial['first_name'] = user.first_name
        self.initial['last_name'] = user.last_name
        self.initial['city'] = ci.city
        self.initial['zip_code'] = ci.zip_code
    
    def update_user(self,user):
        """
        Updates the user.
        """
        ci = CanonicalIdentity.objects.get(user=user)
        ci.city = self.cleaned_data.get('city',None)
        ci.zip_code = self.cleaned_data.get('zip_code',None)
        ci.save()
        
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

grant_choices = (
    ('permitted','Permitted'),
    ('not permitted','Not Permitted'),
)

letter_grade_choices = (
    ('A','A'),
    ('B','B'),
    ('C','C'),
)

specific_choices = (
    ('C','C grade or better data consumers'),
    ('B','B grade or better data consumers'),
    ('A','A grade data consumers only'),
    ('no','Nobody may access this data.'),
)

class PolicyForm(forms.Form):
    """
    Form for a data policy.
    """
    grant = forms.CharField(widget=forms.RadioSelect(choices=specific_choices))

    def init(self,policy):
        """
        Initializes the form.
        """
        self.initial['grant'] = policy.minimum_grade if policy.default_grant else 'no'
    
    def update_policy(self,policy):
        """
        Saves the form data.
        """
        grant = self.cleaned_data['grant']
        if grant != 'no':
            policy.default_grant = True
            policy.minimum_grade = grant
        else:
            policy.default_grant = False
            policy.minimum_grade = None
        policy.save()

class IdentityForm(forms.Form):
    """
    A form for an identity claim.
    """
    service = forms.ModelChoiceField(queryset=Service.objects.all(),empty_label='Choose a Service')
    identity = forms.CharField()
    
    def add_identity(self,user):
        """
        Adds a new identity.
        """
        ci = CanonicalIdentity.objects.get(user=user)
        identity, created = Identity.objects.get_or_create(service=self.cleaned_data['service'],identity=self.cleaned_data['identity'])
        if created:
            IdentityClaim.objects.create(canonical_identity=ci,identity=identity,claim_confidence=75)
        else:
            claim_count = identity.identity_claims.count()
            claim_confidence = min(100 / claim_count,75) if claim_count else 75
            IdentityClaim.objects.create(canonical_identity=ci,identity=identity,claim_confidence=claim_confidence)


class ExceptionForm(forms.Form):
    """
    A form for a policy exception.
    """
    consumer = forms.ModelChoiceField(queryset=DataConsumer.objects.all(),empty_label='Choose a data consumer')
    grant = forms.CharField(widget=forms.RadioSelect(choices=grant_choices))
    scope = forms.ModelChoiceField(queryset=DataScope.objects.all(),empty_label='All Data',required=False)
    
    def add_exception(self,user):
        """
        Adds an exception.
        """
        ci = CanonicalIdentity.objects.get(user=user)
        PolicyException.objects.create(canonical_identity=ci,
                                       consumer=self.cleaned_data['consumer'],
                                       scope=self.cleaned_data['scope'],
                                       grant=True if self.cleaned_data['grant'] == 'permitted' else False)




class SpecificPolicyForm(forms.Form):
    """
    Form for a specific policy.
    """
    scope = forms.ModelChoiceField(queryset=DataScope.objects.all(),empty_label='Choose a data type')
    grant = forms.CharField(widget=forms.RadioSelect(choices=specific_choices))
    
    def add_specific(self,user):
        """
        Creates a specific policy for the specified user.
        """
        ci = CanonicalIdentity.objects.get(user=user)
        granted = self.cleaned_data['grant'] != 'no'
        min_grade = self.cleaned_data['grant'] if granted else None
        PolicyElement.objects.create(canonical_identity=ci,
                                     scope=self.cleaned_data['scope'],
                                     default_grant=granted,
                                     minimum_grade=min_grade)
        