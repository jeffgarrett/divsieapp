from pyramid.config import Configurator
from resources import Root
import views
import pyramid_jinja2
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

def make_app():
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=Root)
    #config.add_tween('divsieapp.timing_tween_factory')
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
