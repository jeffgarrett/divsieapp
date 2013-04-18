from google.appengine.ext import ndb

class Task(ndb.Model):
    user_id = ndb.IntegerProperty()
    user_context = ndb.StringProperty()

    title = ndb.StringProperty()
    description = ndb.StringProperty()

    tags = ndb.StringProperty(repeated=True)

    def __json__(self, request):
        return {
                'user_id': self.user_id,
                'user_context': self.user_context,
                'title': self.title,
                'description': self.description,
                'tags': self.tags
                }


    # status = completed or not
    # completion time
    # last modified time?
    # priority
    # rtm uid

    # meta?

    #notes
    #due date
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
