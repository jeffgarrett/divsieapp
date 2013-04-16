from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.security import remember, Authenticated
from divsieapp.lib.oauth2 import GoogleOAuth2, OAuth2Error
from divsieapp.models import InvitationRequest
from auth import login_view, logout_view

def my_view(request):
    ga = GoogleOAuth2("https://divsieapp.appspot.com/login", prompt="select_account")
    return {'project':'divsieapp', 'auth_url':ga.get_auth_url(), 'user':
            request.user}

def request_invite_view(request):
    email = request.POST.get('email')
    req = InvitationRequest.from_email(email)
    return {'project':'divsieapp', 'email':email}

def notfound(request):
    request.response.status = "404 Not Found"
    return {}

def add_views(config):
    """
    Configure all views.

    Note: config.scan() throws errors on app engine.
    """
    config.add_view(login_view,
                    route_name='login',
                    renderer='landing_page.html')
    config.add_view(logout_view,
                    route_name='logout',
                    renderer='landing_page.html')
    config.add_view(request_invite_view,
                    route_name='request-invite',
                    renderer='request-invite.html')
    config.add_view(my_view,
                    route_name='root',
                    effective_principals=['g:invited'],
                    renderer='landing_page.html')
    config.add_view(my_view,
                    route_name='root',
                    effective_principals=Authenticated,
                    renderer='invitation-code.html')
    config.add_view(my_view,
                    route_name='root',
                    renderer='landing_page.html')
