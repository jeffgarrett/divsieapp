from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from divsieapp.lib.oauth2 import GoogleOAuth2, OAuth2Error

def my_view(request):
    ga = GoogleOAuth2("https://divsieapp.appspot.com/login", prompt="select_account")
    return {'project':'divsieapp', 'auth_url':ga.get_auth_url()}

def request_invite_view(request):
    email = request.POST.get('email')
    usr = User.from_email(email)
    return {'project':'divsieapp', 'email':email}

def login_view(request):
    ga = GoogleOAuth2("https://divsieapp.appspot.com/login", prompt="select_account")
    try:
        ga.handle_redirect_uri(request)
        userinfo = ga.request_userinfo()
    except OAuth2Error:
        pass
    raise HTTPFound("/")

def notfound(request):
    request.response.status = "404 Not Found"
    return {}
