from google.appengine.ext import ndb
from cornice.resource import resource, view
from divsieapp import models
from divsieapp.lib import calendar
import logging


@resource(collection_path='/api/v1/tasks', path='/api/v1/tasks/{id}')
class Task(object):
    def __init__(self, request):
        self.request = request

    @view(renderer='json')
    def collection_get(self):
        try:
            offset = int(self.request.GET.getone('offset'))
        except:
            offset = 0
        tasks = models.Task.query().order(models.Task.title).fetch(20, offset=offset)
        return { "tasks": tasks }

    @view(accept='text/calendar', renderer='json')
    def collection_post(self):
        # if not self.request.user...
        tasks = calendar.parse(self.request.text)

        updated_models = []
        for task in tasks:
            # Set up the task data model
            t = models.Task()
            t.user_id = self.request.user.key.integer_id()
            t.title = task.get('SUMMARY')
            t.description = task.get('DESCRIPTION')
            t.tags = task.get('TAGS')
            updated_models.append(t)
        ndb.put_multi(updated_models)
        return {}

