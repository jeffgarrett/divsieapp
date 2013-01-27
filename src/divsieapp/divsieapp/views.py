from pyramid.httpexceptions import HTTPNotFound
from models import User

def my_view(request):
    return {'project':'divsieapp'}

def request_invite_view(request):
    email = request.POST.get('email')
    usr = User.from_email(email)
    return {'project':'divsieapp', 'email':email}

def notfound(request):
    request.response.status = "404 Not Found"
    return {}
