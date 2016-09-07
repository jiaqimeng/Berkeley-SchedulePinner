from icalendar import Calendar, Event, Timezone, TimezoneStandard, TimezoneDaylight
from dateutil import parser
import re, os, datetime, sys, json, pytz

# change the following numbers in every semester
# FALL_2016_END = datetime.datetime(2016, 12, 3, 0, 0, 0)
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
    return courses

def parse_weekdays(weekdays):
    weekdays_parsed = []
    for i in range(len(weekdays)):
        if weekdays[i] == 'T':
            if i < len(weekdays) - 1 and weekdays[i + 1] == 'h':
                weekdays_parsed.append('th')
            else:
                weekdays_parsed.append('tu')
        if weekdays[i] == 'M':
            weekdays_parsed.append('mo')
        if weekdays[i] == 'W':
            weekdays_parsed.append('we')
        if weekdays[i] == 'F':
            weekdays_parsed.append('fr')
    return weekdays_parsed

# Map weekday string to number. This function is currently only called from parse_time(...)
def weekday_to_num(weekdaystring):
    wdict = {"mo": 0, "tu": 1, "we": 2, "th": 3, "fr": 4}
    return wdict[weekdaystring]

# Round minutes into nearse 5th, i.e 8:59am to 9:00am, 5:29pm to 5:30pm, 8:45am remains the same.
def round_time(hour, minutes):
    hour = int(hour)
    minutes = int(minutes)
    minutes = (minutes + 1) / 5 * 5
    if minutes == 60:
        hour += 1
        minutes = 0
    return datetime.time(hour, minutes)

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
    pacific_time = pytz.timezone('America/Los_Angeles')
    for course, info in scrap_data().iteritems():
        summary = course
        meetings = info["meetings"]
        # location = info["meetings"]
        if len(meetings) > 0:
            main_meeting = meetings[0]
            if not main_meeting["start_time"] or not main_meeting["end_time"]:
                continue
            location = main_meeting["location"]
            weekdays = parse_weekdays(main_meeting["days"])
            date_start, date_end = parser.parse(main_meeting["start_date"]), parser.parse(main_meeting["end_date"])
            
            tstart, tend = round_time(str(main_meeting["start_time"])[:-2], str(main_meeting["start_time"])[-2:]), round_time(str(main_meeting["end_time"])[:-2], str(main_meeting["end_time"])[-2:])
            dtstart = pacific_time.localize(date_start.replace(hour = tstart.hour, minute = tstart.minute, tzinfo = None))
            dtend = pacific_time.localize(date_start.replace(hour = tend.hour, minute = tend.minute, tzinfo = None))
            date_end = pacific_time.localize(date_end.replace(hour = tend.hour, minute = tend.minute, tzinfo = None)) + datetime.timedelta(days = 1)

            rule = ['weekly', weekdays, date_end, 'su']
            event = create_event(uid, dtstart, dtend, location, rule, summary)
            cal.add_component(event)
            uid += 1
    cal.add('X-WR-TIMEZONE', "America/Los_Angeles")
    path = os.getcwd() + "/FA16 Schedule.ics"
    if getattr(sys, 'frozen', False):
        path = os.path.dirname(sys.executable) + "/FA16 Schedule.ics"
    write_to_file(cal, path)


main()
