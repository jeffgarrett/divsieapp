from pyramid.config import Configurator
from resources import Root
import views
import pyramid_jinja2
import os

__here__ = os.path.dirname(os.path.abspath(__file__))


def make_app():
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=Root)
    config.add_renderer('.html', pyramid_jinja2.Jinja2Renderer)
    config.add_notfound_view(views.my_view, renderer='404.html')
    config.add_view(views.my_view,
                    context=Root,
                    renderer='mytemplate.html')
    return config.make_wsgi_app()

application = make_app()
