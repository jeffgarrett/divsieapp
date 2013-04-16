from google.appengine.ext import ndb

class InvitationRequest(ndb.Model):
    email = ndb.StringProperty()

    # Invitations:
    #   time of first request, number of requests, generated code
    invitation_req_first_time = ndb.DateTimeProperty(auto_now_add=True)
    invitation_req_count = ndb.IntegerProperty(default=1)
    invitation_code = ndb.StringProperty()

    @classmethod
    @ndb.transactional
    def from_email(cls, email):
        key = ndb.Key(InvitationRequest, str(email))
        req = key.get()
        if req is None:
            req = InvitationRequest(key=key, email=email)
        else:
            req.invitation_req_count += 1
        req.put()
        return req
