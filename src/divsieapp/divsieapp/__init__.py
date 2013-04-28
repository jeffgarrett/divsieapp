# Cornice will import simplejson which fails. Fake it.
import sys, json
sys.modules['simplejson'] = json

from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import unauthenticated_userid

import uuid
import cornice
from resources import Root
import models
import views
import pyramid_jinja2
from divsieapp.models import Secret
import os, time, logging

import api_v1

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
    userid = unauthenticated_userid(request)
    if userid is not None:
        return models.User.from_identity(userid)

def groupfinder(userid, request):
    usr = request.user
    if not usr:
        return None
    if not usr.invited:
        return []
    return ['g:invited']

def make_app():
    """ This function returns a Pyramid WSGI application.
    """

    auth_secret = Secret.get_secret('auth_secret')
    if not auth_secret.value:
        auth_secret.value = uuid.uuid4().hex
        auth_secret.put()

    authn_policy = AuthTktAuthenticationPolicy(
                       auth_secret.value,
                       callback=groupfinder,
                       cookie_name='divsie_auth',
                       secure=True,
                       timeout=86400,
                       reissue_time=300,
                       max_age=86400,
                       http_only=True,
                       wild_domain=False,
                   )
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(root_factory=Root,
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy)


    #config.add_tween('divsieapp.timing_tween_factory')
    config.add_request_method(get_user, 'user', reify=True)
    config.add_renderer('.html', pyramid_jinja2.Jinja2Renderer)
    config.add_notfound_view(views.notfound, renderer='404.html')

    # The root page, which may be different based on user status.
    config.add_route('root', '/')

    # The form target to request an invite code.
    config.add_route('request-invite', '/request-invite')
    # The form target to redeem an invite code.
    config.add_route('invitation-code', '/invitation-code')

    # The targets which actually log a user in or out.
    # The login target expects proof of identity.
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

    # Hook up the views
    views.add_views(config)

    config.include(cornice)
    config.include(api_v1)

    return config.make_wsgi_app()

def webapp_add_wsgi_middleware(app):
    from google.appengine.ext.appstats import recording
    app = recording.appstats_wsgi_middleware(app)
    return app

application = make_app()
application = webapp_add_wsgi_middleware(application)
