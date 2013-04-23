class Filter:
    def __init__(self, filterstr):
        self.filterstr = filterstr

    def match(self, task):
        # simple matching
        if task.title.lower().find(self.filterstr.lower()) != -1:
            return True
        return False
