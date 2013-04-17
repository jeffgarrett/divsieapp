from cornice.resource import resource, view

TASKS = { 1: [ 'hey' ] }

@resource(collection_path='/api/v1/tasks', path='/api/v1/tasks/{id}')
class Task(object):
    def __init__(self, request):
        self.request = request

    @view(renderer='json')
    def collection_get(self):
        return TASKS

    @view(accept='text/calendar', renderer='json')
    def collection_post(self):
        return TASKS
