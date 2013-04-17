from google.appengine.ext import ndb

class Task(ndb.Model):
    user_id = ndb.IntegerProperty()
    user_context = ndb.StringProperty()

    title = ndb.StringProperty()
    description = ndb.StringProperty()

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
