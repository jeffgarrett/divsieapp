from google.appengine.ext import ndb
from identity import ExternalIdentity

class User(ndb.Model):
    display_name = ndb.StringProperty()

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
