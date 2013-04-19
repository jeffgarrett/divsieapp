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
    def collection_delete(self):
        # if not self.request.user...
        user_id = self.request.user.key.integer_id()
        tasks = models.Task.query(models.Task.user_id == user_id).fetch()
        ndb.delete_multi([x.key for x in tasks])
        return {}

    @view(renderer='json')
    def collection_get(self):
        # if not self.request.user...
        user_id = self.request.user.key.integer_id()
        try:
            offset = int(self.request.GET.getone('offset'))
        except:
            offset = 0
        try:
            completed = bool(int(self.request.GET.getone('completed')))
        except:
            completed = False
        tasks = models.Task.query(models.Task.user_id == user_id,
                                  models.Task.completed == completed).order(models.Task.title).fetch(20, offset=offset)
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
            t.completed = (task.get('STATUS') == 'COMPLETED')
            t.completion_time = task.get('COMPLETED')
            t.last_modification_time = task.get('LAST-MODIFIED')
            t.due_time = task.get('DUE')
            t.title = task.get('SUMMARY')
            t.description = task.get('DESCRIPTION')
            t.tags = task.get('TAGS')
            t.priority = task.get('PRIORITY')
            updated_models.append(t)
        ndb.put_multi(updated_models)
        return {}
