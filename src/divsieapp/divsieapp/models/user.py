from google.appengine.ext import ndb
from identity import ExternalIdentity
import datetime, logging

class User(ndb.Model):
    display_name = ndb.StringProperty()

    #external_identity = ndb.StructuredProperty(ExternalIdentity)
    primary_email = ndb.StringProperty()

    # Invitations:
    #   time of first request, number of requests, generated code
    invitation_req_first_time = ndb.DateTimeProperty(auto_now_add=True)
    invitation_req_count = ndb.IntegerProperty(default=1)
    invitation_code = ndb.StringProperty()

    @classmethod
    @ndb.transactional
    def from_email(cls, email):
        key = ndb.Key(User, str(email))
        usr = key.get()
        if usr is None:
            usr = User(key=key, primary_email=email)
        else:
            usr.invitation_req_count += 1
        usr.put()
        return usr

    @classmethod
    def from_identity(cls, s):
        identity = ExternalIdentity.from_string(s)
        if not identity:
            return None
        key = ndb.Key(User, identity.user_id)
        return key.get()
