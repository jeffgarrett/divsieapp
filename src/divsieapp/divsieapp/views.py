from pyramid.httpexceptions import HTTPNotFound

def my_view(request):
    return {'project':'divsieapp'}

def notfound(request):
     return HTTPNotFound()
