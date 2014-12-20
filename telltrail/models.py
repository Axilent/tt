"""
Models for TellTrail.
"""
from django.db import models
from django.contrib.auth.models import User

class CanonicalIdentityManager(models.Manager):
    """
    Manager class for CanonicalIdentity.
    """
    def filter_by_identity(self,identity):
        """
        Retrieves CanonicalIdentity objects by associated service identities.
        """
        return self.filter(pk__in=[claim.pk for claim in IdentityClaim.objects.filter(identity=identity)])
    
    def get_by_identity(self,identity):
        """
        Gets a single CanonicalIdentity by the specified service identity.  Will raise an exception
        if there is more than one claim on the identity.
        """
        return IdentityClaim.objects.get(identity=identity).canonical_identity

class CanonicalIdentity(models.Model):
    """
    The definitive identity of a user.
    """
    user = models.ForeignKey(User,unique=True)
    city = models.CharField(null=True, max_length=100)
    zip_code = models.CharField(null=True, max_length=10)
    
    objects = CanonicalIdentityManager()
    
    def __unicode__(self):
        return self.user.username
    
    @property
    def default_policy(self):
        """
        Gets the default policy.
        """
        policy, created = self.policy_elements.get_or_create(scope__isnull=True)
        if created:
            policy.minimum_grade = 'C'
            policy.save()
        return policy
    
    @property
    def specific_policies(self):
        """
        Retrieves policy elements with specific data scope.
        """
        return self.policy_elements.filter(scope__isnull=False)
    
    def render_policy(self):
        """
        Renders the policy into a structure suitable for JSON serialization.
        """
        # Personal Info
        policy = {'username':self.user.username,'first_name':self.user.first_name,'last_name':self.user.last_name}
        if self.city:
            policy['city'] = self.city
        if self.zip_code:
            policy['zip_code'] = self.zip_code
        
        # Identities
        identities = []
        for claim in self.identity_claims.all():
            rendered_identity = {'identity':claim.identity.identity,
                                 'service':claim.identity.service.name,
                                 'profile':claim.identity.profile,
                                 'confidence':claim.claim_confidence}
            identities.append(rendered_identity)
        policy['identities'] = identities
        
        # Default Policy
        default_policy = self.default_policy
        policy['default_grant'] = default_policy.default_grant
        policy['minimum_grade'] = default_policy.minimum_grade
        
        # Exceptions
        exceptions = []
        for policy_exception in self.policy_exceptions.all():
            rendered_exception = {'grant':policy_exception.grant,
                                  'consumer':{'name':policy_exception.consumer.name,'domain':policy_exception.consumer.domain}}
            if policy_exception.scope:
                rendered_exception['scope'] = unicode(policy_exception.scope)
            exceptions.append(rendered_exception)
        policy['exceptions'] = exceptions
        
        
        # Specific Policies
        specific_policies = []
        for specific_policy in self.specific_policies:
            specific_policies.append({'scope':unicode(specific_policy.scope),
                                      'grant':specific_policy.default_grant,
                                      'minimum_grade':specific_policy.minimum_grade})
        policy['specific_policies'] = specific_policies
        
        return policy

class Service(models.Model):
    """
    An internet service on which someone may have an identity.
    """
    name = models.CharField(unique=True, max_length=100)
    url = models.URLField(blank=True,)
    verified = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.name

class Identity(models.Model):
    """
    An identity at a service.
    """
    service = models.ForeignKey(Service,related_name='identities')
    identity = models.CharField(max_length=100)
    profile = models.CharField(max_length=100)
    
    def __unicode__(self):
        return '%s@%s' (unicode(self.identity),unicode(self.service))
    
    class Meta:
        unique_together = (('service','identity'),)

class IdentityClaim(models.Model):
    """
    A canonical identity that claims an identity.
    """
    canonical_identity = models.ForeignKey(CanonicalIdentity,related_name='identity_claims')
    identity = models.ForeignKey(Identity,related_name='identity_claims')
    claim_confidence = models.IntegerField()

class DataConsumer(models.Model):
    """
    A consumer of data.
    """
    name = models.CharField(max_length=100)
    domain = models.URLField()
    letter_grade = models.CharField(max_length=1,default='C')
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        unique_together = (('name','domain'),)

class DataScope(models.Model):
    """
    A topical category for data, such as 'clothing', 'books' or 'social',
    that can be used as a scope for a policy element.
    """
    name = models.CharField(primary_key=True, max_length=100)
    parent = models.ForeignKey('self',null=True)
    
    def __unicode__(self):
        if self.parent:
            return '%s : %s' % (unicode(self.parent),self.name)
        else:
            return self.name

class PolicyElement(models.Model):
    """
    An element of a user's data policy.
    """
    canonical_identity = models.ForeignKey(CanonicalIdentity,related_name='policy_elements')
    scope = models.ForeignKey(DataScope,null=True)
    default_grant = models.BooleanField(default=True) # If true, data in this scope is granted, otherwise not.  Overriden by service lists.
    minimum_grade = models.CharField(null=True, max_length=1) # if not null, the minimum grade to which the grant is offered
    
    class Meta:
        unique_together = (('canonical_identity','scope'),)

class PolicyException(models.Model):
    """
    A policy for a specific data consumer.
    """
    canonical_identity = models.ForeignKey(CanonicalIdentity,related_name='policy_exceptions')
    scope = models.ForeignKey(DataScope,null=True)
    consumer = models.ForeignKey(DataConsumer)
    grant = models.BooleanField(default=True) # If true, this is a specific grant to the consumer, if false it is a specific denial.
    
    class Meta:
        unique_together = (('canonical_identity','consumer','scope'),)

class DataSource(models.Model):
    """
    A source of data.
    """
    account_name = models.CharField(max_length=100)
    instance_name = models.CharField(max_length=100)
    api_key = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    
    def __unicode__(self):
        return '%s:%s' % (self.account_name,self.instance_name)
    
    class Meta:
        unique_together = (('account_name','instance_name'),)
