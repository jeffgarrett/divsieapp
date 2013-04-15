from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.security import remember
from divsieapp.lib.oauth2 import GoogleOAuth2, OAuth2Error
from divsieapp.models.user import User
from auth import login_view, logout_view

def my_view(request):
    ga = GoogleOAuth2("https://divsieapp.appspot.com/login", prompt="select_account")
    return {'project':'divsieapp', 'auth_url':ga.get_auth_url(), 'user':
            request.user}

def request_invite_view(request):
    email = request.POST.get('email')
    usr = User.from_email(email)
    return {'project':'divsieapp', 'email':email}

def notfound(request):
    request.response.status = "404 Not Found"
    return {}
