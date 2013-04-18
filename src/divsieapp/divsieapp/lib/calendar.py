import icalendar

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
                task[key] = val.dt
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

        tasks.append(task)
    return tasks

#298 COMPLETED
#895 DESCRIPTION
#895 DTSTAMP
#9 DTSTART
#895 DTSTART;TZID=America/Chicago
#27 DUE
#251 DUE;VALUE=DATE
#906 END
#896 LAST-MODIFIED
#13 PRIORITY
#178 RDATE;VALUE=DATE-TIME
#91 RRULE
#895 SEQUENCE
#298 STATUS
#895 SUMMARY
#9 TZNAME
#9 TZOFFSETFROM
#9 TZOFFSETTO
#895 UID
# 3 URL;VALUE=URI
