from pyramid.httpexceptions import HTTPNotFound

def my_view(request):
    return {'project':'divsieapp'}

def request_invite_view(request):
    return {'project':'divsieapp', 'email':request.POST.get('email')}

def notfound(request):
    request.response.status = "404 Not Found"
    return {}
