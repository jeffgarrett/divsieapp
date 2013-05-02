from pyramid.renderers import JSON

class SafeJSON(JSON):
    def __call__(self, info):
        _render = super(SafeJSON, self).__call__(info)
        def _wrapper(value, system):
            request = system.get('request')
            return ")]}',\n" + _render(value, system)
        return _wrapper
