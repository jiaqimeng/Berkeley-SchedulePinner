from icalendar import Calendar, Event, Timezone, TimezoneStandard, TimezoneDaylight
from dateutil import *
import re, os, datetime, sys, json

# change the following numbers in every semester
FALL_2016_END = datetime.datetime(2016, 12, 3, 0, 0, 0)
FALL_2016_START_YEAR = 2016
FALL_2016_START_MONTH = 8
FALL_2016_START_DAY = 23 # this is intended set to be 1 day less than instruction date
PRODUCT_ID = '-//M & Z Product//Berkeley iCal//EN'


# Display the calendar in a friendly format
def display(cal):
    return cal.to_ical().replace('\r\n', '\n').strip()

# Create the event based on several factors
def create_event(uid, dtstart, dtend, location, rule, summary):
    event = Event()
    event['uid'] = uid
    event.add('dtstart', dtstart)
    event.add('dtend', dtend)
    event['location'] = location
    event['summary'] = summary
    event.add('rrule', create_event_rule(rule[0], rule[1], rule[2], rule[3]))
    return event

# Create the event rule, this function is currently only called by create_event(...)
def create_event_rule(frequency, byday, until, weekdaystarts):
    return {'freq': frequency, 'byday': byday,
            'until': until, 'WKST': weekdaystarts}

# Set up the default timezone, which is USA/LA, and the daylight saving start time and end time.
def create_default_timezone():
    timezone = Timezone()
    timezone['TZID'] = 'America/Los_Angeles'

    timezone_standard = TimezoneStandard()
    timezone_standard['dtstart'] = '19701101T020000'
    timezone_standard.add('rrule', {'freq': 'yearly', 'bymonth': 11, 'byday': '1su'})
    timezone_standard['tzname'] = 'PST'
    timezone_standard['tzoffsetfrom'] = '-0700'
    timezone_standard['tzoffsetto'] = '-0800'

    timezone_daylight = TimezoneDaylight()
    timezone_daylight['dtstart'] = '19700308T020000'
    timezone_daylight.add('rrule', {'freq': 'yearly', 'bymonth': 3, 'byday': '2SU'})
    timezone_daylight['TZNAME'] = 'PDT'
    timezone_daylight['tzoffsetfrom'] = '-0800'
    timezone_daylight['tzoffsetto'] = '-0700'

    timezone.add_component(timezone_standard)
    timezone.add_component(timezone_daylight)
    timezone['X-LIC-LOCATION'] = 'America/Los_Angeles'
    return timezone

# Scrap data from the .htm file and put it into dictionary format.
def scrap_data():
    current_dir = os.getcwd() + "/"
    if getattr(sys, 'frozen', False):
        current_dir = os.path.dirname(sys.executable) + "/"
    try:
        html = open(current_dir + "Schedule Planner.html")
    except IOError:
        try: 
            html = open(current_dir + "Schedule Planner.htm")
        except IOError:
            print("Unexpected error: Could not find Schedule Planner file")
            raise
    m = re.findall('jsonData = (.*?);\s*Scheduler.initialize', html.read().replace('\n', ''))
    data = json.loads(m[0])
    courses = {}
    for course in data['currentSectionData']:
        subject = course['subjectId']
        number = course['course']
        component = course['component']
        section = course['sectionNumber']
        if (len(course['instructor'])) == 0:
            instructor = ""
        else:
            instructor = course['instructor'][0]['id']
        meetings = []
        for meeting in course['meetings']:
            this_meeting = {
                "days" : meeting['days'],
                "start_time" : meeting['startTime'],
                "end_time" : meeting['endTime'],
                "location" : meeting['location'],
                "start_date" : meeting['startDate'],
                "end_date" : meeting['endDate']
            }
            meetings.append(this_meeting)
        # construct object
        this_course = {"subject": subject, "number": number, "component": component, "instructor": instructor,
                        "meetings": meetings}
        courses[subject + " " + number + " " + component] = this_course
        print(courses)
    return courses
    

# Parse raw time string into a tuple which contains dtstart, dtend and weekdays
def parse_time(time):
    contents = time.split()
    weekdays = []
    contents_weekdays = contents[0]
    for i in range(len(contents_weekdays)):
        if contents_weekdays[i] == 'T':
            if i < len(contents_weekdays) - 1 and contents_weekdays[i + 1] == 'h':
                weekdays.append('th')
            else:
                weekdays.append('tu')
        if contents_weekdays[i] == 'M':
            weekdays.append('mo')
        if contents_weekdays[i] == 'W':
            weekdays.append('we')
        if contents_weekdays[i] == 'F':
            weekdays.append('fr')
    t_start = contents[1].split(':')
    t_end = contents[3].split(':')
    t_start_parsed = parse_hour_minute(t_start)
    t_end_parsed = parse_hour_minute(t_end)
    t_start_adjusted = datetime.date(2070, 1, 1)
    for i in weekdays:
        temp = next_weekday(datetime.date(FALL_2016_START_YEAR, FALL_2016_START_MONTH, FALL_2016_START_DAY), weekday_to_num(i))
        if temp < t_start_adjusted:
            t_start_adjusted = temp
    dtstart = datetime.datetime(t_start_adjusted.year, t_start_adjusted.month, t_start_adjusted.day,
                                t_start_parsed[0], t_start_parsed[1], 0)
    dtend = datetime.datetime(t_start_adjusted.year, t_start_adjusted.month, t_start_adjusted.day,
                              t_end_parsed[0], t_end_parsed[1], 0)
    # dtstart and dtend are datetime classes. weekdays is a list of string, i.e ['mo', 'tu', 'we'...]
    return (dtstart, dtend, weekdays)

# Turn 12-hour format into 24-hour format. This function is currently only called from parse_time(...)
def parse_hour_minute(t):
    am_pm = t[1][len(t[1]) - 2:len(t[1])]
    hour, minutes = round_time(int(t[0]), int(t[1][0:2]))
    if am_pm == "pm" and hour < 12:
        hour += 12
    return (hour, minutes)

# Map weekday string to number. This function is currently only called from parse_time(...)
def weekday_to_num(weekdaystring):
    if weekdaystring == "mo":
        return 0
    if weekdaystring == "tu":
        return 1
    if weekdaystring == "we":
        return 2
    if weekdaystring == "th":
        return 3
    if weekdaystring == "fr":
        return 4

# Round minutes into nearse 5th, i.e 8:59am to 9:00am, 5:29pm to 5:30pm, 8:45am remains the same.
def round_time(hour, minutes):
    minutes = (minutes + 1) / 5 * 5
    if minutes == 60:
        hour += 1
        minutes = 0
    return (hour, minutes)

# Get next weekday starting from date d. Return a datetime class.
def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

# write the calendar to .ics file.
def write_to_file(calendar, path):
    f = open(path, "w")
    f.write(calendar.to_ical())
    f.close()


def main():
    cal = Calendar()
    cal['version'] = '2.0'
    cal.add('prodid', PRODUCT_ID)
    cal.add_component(create_default_timezone())
    uid = 1
    for course, info in scrap_data().iteritems():
        summary = course
        location = info["location"]
        time_parsed = parse_time(info["time"])
        dtstart = time_parsed[0]
        dtend = time_parsed[1]
        rule = ['weekly', time_parsed[2], FALL_2016_END, 'su']
        event = create_event(uid, dtstart, dtend, location, rule, summary)
        cal.add_component(event)
        uid += 1
    cal.add('X-WR-TIMEZONE', "America/Los_Angeles")
    path = os.getcwd() + "/FA16 Schedule.ics"
    if getattr(sys, 'frozen', False):
        path = os.path.dirname(sys.executable) + "/FA16 Schedule.ics"
    write_to_file(cal, path)


main()
