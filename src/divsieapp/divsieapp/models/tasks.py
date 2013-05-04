from google.appengine.ext import ndb

class Task(ndb.Model):
    # Owner
    user_id = ndb.IntegerProperty()
    # Contextual intelligence, one day
    user_context = ndb.StringProperty()
    # Currently being worked on (or momentarily paused)
    active = ndb.BooleanProperty(default=False)
    # Completion
    completed = ndb.BooleanProperty()
    completion_time = ndb.DateTimeProperty()
    # Creation, modification
    creation_time = ndb.DateTimeProperty()
    modification_time = ndb.DateTimeProperty()
    # Due
    due_time = ndb.DateTimeProperty()
    # Time estimate, in minutes
    time_estimate = ndb.IntegerProperty()
    # Text content
    content = ndb.StringProperty()
    # Tags
    tags = ndb.StringProperty(repeated=True)
    # Priority
    priority = ndb.FloatProperty()

    def __json__(self, request):
        value = {
            'id': self.key.integer_id(),
            'user_context': self.user_context,
            'active': self.active,
            'completed': self.completed,
            'time_estimate': self.time_estimate,
            'content': self.content,
            'tags': self.tags,
            'priority': self.priority
        }
        for attr in ('completion_time',
                     'creation_time',
                     'modification_time',
                     'due_time'):
            u = getattr(self, attr, None)
            if u:
                u = u.isoformat(' ')
            value[attr] = u
        return value


    # more general status than completed/not?
    # rtm uid
    # meta?
    #notes
    #repeat
    #location
    #url
    #completed vs not?
    #postponed (# times)
    #shared with
    #subtasks / blocked on (parent/child, dependencies)
    #system estimated time
