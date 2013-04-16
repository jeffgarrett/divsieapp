from google.appengine.ext import ndb
import datetime, user


class ExternalIdentity(ndb.Model):
    user_id = ndb.IntegerProperty()
    provider = ndb.StringProperty()
    identity = ndb.StringProperty()

    @classmethod
    def from_string(cls, s):
        try:
            parts = s.split(':')
            provider_str = parts[0]
            provider_cls = providers[provider_str]
            identity_str = ':'.join(parts[1:])
            key = ndb.Key(provider_cls, str(identity_str))
            return key.get()
        except:
            return None

    def __str__(self):
        return self.provider + ':' + self.identity

class GoogleIdentity(ExternalIdentity):
    email = ndb.StringProperty()
    verified_email = ndb.BooleanProperty()

    @classmethod
    @ndb.transactional(xg=True)
    def from_userinfo(cls, ui):
        provider = 'Google'
        identity = ui['id']
        key = ndb.Key(GoogleIdentity, str(identity))
        uid = key.get()
        if uid is None:
            usr = user.User(display_name=ui['email'])
            user_id = usr.put().integer_id()
            uid = GoogleIdentity(key=key,
                    user_id=user_id,
                    provider=provider,
                    identity=identity,
                    email=ui['email'],
                    verified_email=ui['verified_email'])
            uid.put()
        return uid

providers = {
        'Google': GoogleIdentity
        }
