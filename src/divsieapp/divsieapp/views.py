from pyramid.httpexceptions import HTTPNotFound

def my_view(request):
    return {'project':'divsieapp'}

def notfound(request):
    request.response.status = "404 Not Found"
    return {}
