"""
Handlers for TellTrail API.
"""
from piston.handler import BaseHandler
from piston.utils import rc
from telltrail.models import Identity, DataSource, Service
from itertools import chain

class PolicyHandler(BaseHandler):
    """
    Handler for data policies.
    """
    allow_methods = ('GET','POST')
    
    def process_profile(self,profile):
        """
        Processes a single profile.
        """
        try:
            identity = Identity.objects.get(profile=profile)
            return [claim.canonical_identity.render_policy() for claim in identity.identity_claims.all()]
        except Identity.DoesNotExist:
            return []
    
    def process_profile_list(self,profile_list):
        """
        Processes a list of profiles.
        """
        identities = Identity.objects.filter(profile__in=profile_list)
        return [claim.canonical_identity.render_policy() for claim in chain(*[identity.identity_claims.all() for identity in identities])]
    
    def process_identity(self,identity_string):
        """
        Processes an identity string.
        """
        identity_name, service_name = identity_string.split('@@')
        try:
            identity = Identity.objects.get(service__name__iexact=service_name,identity__iexact=identity_name)
            return [claim.canonical_identity.render_policy() for claim in identity.identity_claims.all()]
        except Identity.DoesNotExist:
            return []
    
    def process_identity_list(self,identity_list):
        """
        Processes a list of identity strings.
        """
        policy_list = []
        for identity_string in identity_list.split(','):
            try:
                print 'identity string',identity_string
                identity_name, service_name = identity_string.split('@@')
                identity = Identity.objects.get(identity__iexact=identity_name,service__name__iexact=service_name)
                policy_list += [claim.canonical_identity.render_policy() for claim in identity.identity_claims.all()]
            except Identity.DoesNotExist:
                pass
        return policy_list
    
    def process(self,request,api_key):
        """
        Main processing method.
        
        Will look for the following four lookup variables:
        
        profile
        profile_list
        identity  (syntax: <identity>@@<service>, for example: "LorenDavie@@Twitter")
        identity_list
        
        """
        try:
            source = DataSource.objects.get(api_key=api_key)
            if source.active:
                # source is registered and active, proceed
                policy_list = []
                
                if 'profile' in request.GET:
                    policy_list += self.process_profile(request.GET['profile'])
                
                if 'profile_list' in request.GET:
                    policy_list += self.process_profile_list(request.GET['profile_list'])
                
                if 'identity' in request.GET:
                    policy_list += self.process_identity(request.GET['identity'])
                
                if 'identity_list' in request.GET:
                    policy_list += self.process_identity_list(request.GET['identity_list'])
                
                return policy_list
            else:
                return rc.FORBIDDEN
        except DataSource.DoesNotExist:
            return rc.NOT_FOUND
        
    
    def read(self,request,api_key):
        """
        GET Handler.
        """
        return self.process(request,api_key)
    
    def create(self,request,api_key):
        """
        POST Handler
        """
        return self.process(request,api_key)
