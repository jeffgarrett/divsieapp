from google.appengine.ext import ndb
import datetime

class User(ndb.Model):
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
