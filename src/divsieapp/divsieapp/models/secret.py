from google.appengine.ext import ndb


class Secret(ndb.Model):
    """
    App secret stored in datastore

    e.g.,
    google_developer_key, google_client_id, google_client_secret
    auth_secret (for session cookies)
    """
    name = ndb.StringProperty(required=True)
    value = ndb.StringProperty(indexed=False)

    @classmethod
    @ndb.transactional
    def get_secret(cls, s):
        key = ndb.Key(Secret, str(s))
        sec = key.get()
        if sec is None:
            sec = Secret(key=key, name=s)
            sec.put()
        return sec
