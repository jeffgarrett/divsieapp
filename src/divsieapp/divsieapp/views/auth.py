from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from divsieapp.lib.oauth2 import GoogleOAuth2, OAuth2Error

def login_view(request):
    ga = GoogleOAuth2("https://divsieapp.appspot.com/login", prompt="select_account")
    headers = None
    try:
        ga.handle_redirect_uri(request)
        userinfo = ga.request_userinfo()
        headers = remember(request, userinfo["email"])
        raise HTTPFound("/", headers=headers)
    except OAuth2Error:
        pass
    raise HTTPFound("/")

def logout_view(request):
    if request.user:
        headers = forget(request)
        raise HTTPFound("/", headers=headers)
    raise HTTPFound("/")
