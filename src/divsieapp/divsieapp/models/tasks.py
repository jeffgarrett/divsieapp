from google.appengine.ext import ndb

class Task(ndb.Model):
    user_id = ndb.IntegerProperty()
    user_context = ndb.StringProperty()

    completed = ndb.BooleanProperty()
    completion_time = ndb.DateTimeProperty()
    last_modification_time = ndb.DateTimeProperty()
    due_time = ndb.DateTimeProperty()

    title = ndb.StringProperty()
    description = ndb.StringProperty()

    tags = ndb.StringProperty(repeated=True)

    priority = ndb.FloatProperty()

    def __json__(self, request):
        return {
                'id': self.key.integer_id(),
                'user_id': self.user_id,
                'user_context': self.user_context,
                'completed': self.completed,
                # times
                'title': self.title,
                'description': self.description,
                'tags': self.tags,
                'priority': self.priority
                }


    # more general status than completed/not?
    # rtm uid

    # meta?

    #notes
    #repeat
    #time estimate
    #tags / list
    #location
    #url
    #completed vs not?
    #postponed (# times)
    #shared with
    #subtasks / blocked on (parent/child, dependencies)
    #system estimated time
