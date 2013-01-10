from google.appengine.api import users
import md5

def my_view(request):
    ret = {}

    user = users.get_current_user()
    if user:
        ret['user'] = user.email()
	ret['user_hash'] = md5.new(user.email().lower()).hexdigest()
        #ret['logout_url'] = users.create_logout_url("/")

    else:
        ret['login_url'] = users.create_login_url("/")

    return ret
