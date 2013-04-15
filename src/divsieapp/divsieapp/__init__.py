from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import unauthenticated_userid
from resources import Root
import models
import views
import pyramid_jinja2
from keys import auth_secret
import os, time, logging

__here__ = os.path.dirname(os.path.abspath(__file__))

def timing_tween_factory(handler, registry):
    def timing_tween(request):
        start = time.time()
        try:
            response = handler(request)
        finally:
            end = time.time()
            logging.info('Request took %sms' %
                         int((end - start) * 1000))
        return response
    return timing_tween

def get_user(request):
    email = unauthenticated_userid(request)
    if email is not None:
        return models.User.from_email(email)

def groupfinder(userid, request):
    return None

def make_app():
    """ This function returns a Pyramid WSGI application.
    """
    authn_policy = AuthTktAuthenticationPolicy(
                       auth_secret,
                       callback=groupfinder,
                   )
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(root_factory=Root,
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy)
    #config.add_tween('divsieapp.timing_tween_factory')
    config.add_request_method(get_user, 'user', reify=True)
    config.add_renderer('.html', pyramid_jinja2.Jinja2Renderer)
    config.add_notfound_view(views.notfound, renderer='404.html')

    config.add_route('root', '')
    config.add_route('request-invite', 'request-invite')
    config.add_route('login', 'login')

    config.add_view(views.my_view,
                    route_name='root',
                    renderer='landing_page.html')
    config.add_view(views.request_invite_view,
                    route_name='request-invite',
                    renderer='request-invite.html')
    config.add_view(views.login_view,
                    route_name='login',
                    renderer='landing_page.html')


    return config.make_wsgi_app()

application = make_app()
