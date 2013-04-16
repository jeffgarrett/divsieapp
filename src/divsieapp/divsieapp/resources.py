from pyramid.security import Allow, Everyone, Authenticated, ALL_PERMISSIONS, DENY_ALL

class Root(object):
    __acl__ = [
        (Allow, Everyone, 'public'),
        (Allow, Authenticated, 'create'),
        (Allow, 'g:invited', 'create'),
        (Allow, 'g:editor', 'edit'),
        (Allow, 'g:admin', ALL_PERMISSIONS),
        DENY_ALL
    ]

    def __init__(self, request):
        self.request = request
