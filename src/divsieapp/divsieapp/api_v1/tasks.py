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
        ds_filters = [models.Task.user_id == user_id]

        try:
            completed = (self.request.GET.getone('completed') == "true")
        except:
            completed = False
        ds_filters.append(models.Task.completed == completed)

        try:
            logging.info(self.request.GET.getone('active'))
            active = (self.request.GET.getone('active') == "true")
            ds_filters.append(models.Task.active == active)
        except:
            pass

        try:
            limit = int(self.request.GET.getone('limit'))
            if limit < 10:
                limit = 10
            if limit > 50:
                limit = 50
        except:
            limit = 20

        try:
            offset = int(self.request.GET.getone('offset'))
        except:
            offset = 0

        queries = 1

        more = True
        tasks = models.Task.query(*ds_filters).order(models.Task.title).fetch(limit, offset=offset)
        if not tasks:
            more = False
        offset += limit

        return { "tasks": tasks, "offset": offset, "more": more, "queries": queries }

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
        return { "tasks": updated_models }

    @view(renderer='json')
    def post(self):
        # if not self.request.user...
        task_in = self.request.json_body
        if not task_in.get('id'):
            return
        task = models.Task.get_by_id(task_in.get('id'))
        if not task:
            # problem
            return
        if task.user_id != self.request.user.key.integer_id():
            # problem
            return

        if 'completed' in task_in:
            if task_in['completed'] != task.completed:
                task.completed = task_in['completed']
                task.put()
        if 'active' in task_in:
            if task_in['active'] != task.active:
                task.active = task_in['active']
                task.put()

        return task
