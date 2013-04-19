import datetime, icalendar, pytz

def _extract_fields(lines, prefix):
    vals = []
    for ln in lines:
        if not ln.startswith(prefix):
            continue

        suffix = ln[len(prefix):]
        if suffix.strip() == "none":
            continue

        v = suffix.split(",")
        for u in v:
            vals.append(u.strip())

    lines = [x for x in lines if not x.startswith(prefix)]
    return lines, vals

def parse(text):
    cal = icalendar.Calendar.from_ical(text)
    tasks = []
    for task in cal.walk():
        if not isinstance(task, icalendar.Todo):
            continue

        # Normalize the values
        task = dict(task)
        for key, val in task.items():
            if 'dt' in dir(val):
                d = val.dt
                if isinstance(d, datetime.datetime) and d.tzinfo is not None:
                    d = d.astimezone(pytz.utc)
                    d = d.replace(tzinfo=None)
                task[key] = d
            elif 'title' in dir(val):
                task[key] = str(val)

        # Parse the description
        desc = task.get('DESCRIPTION')
        if desc:
            lines = desc.rstrip().split('\n')
            lines, tags = _extract_fields(lines, 'Tags: ')
            task['TAGS'] = tags
            lines, estimate = _extract_fields(lines, 'Time estimate: ')
            task['ESTIMATE'] = estimate
            lines, location = _extract_fields(lines, 'Location: ')
            task['LOCATION'] = location
            task['DESCRIPTION'] = '\n'.join(lines)

        # Normalize to datetime
        if isinstance(task.get('DUE'), datetime.date):
            task['DUE'] = datetime.datetime.combine(task['DUE'],
                    datetime.time())

        # Rescale priority from 0 to 1 (1 = highest)
        if task.get('PRIORITY'):
            task['PRIORITY'] = (9.0 - task['PRIORITY']) / 8.0

        tasks.append(task)
    return tasks

#895 UID
#895 DTSTAMP - similar to last-modified

# recurrence stuff
#9 DTSTART
#178 RDATE;VALUE=DATE-TIME
#91 RRULE

#895 SEQUENCE
#9 TZNAME
#9 TZOFFSETFROM
#9 TZOFFSETTO
# 3 URL;VALUE=URI
