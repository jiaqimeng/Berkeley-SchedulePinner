from icalendar import Calendar, Event, Timezone, TimezoneStandard, TimezoneDaylight; from dateutil import *
import re, bs4, os, datetime

# return a .ics formatted string
FALL_2016_END = datetime.datetime(2016, 12, 3, 0, 0, 0)
FALL_2016_START_YEAR = 2016
FALL_2016_START_MONTH = 8
FALL_2016_START_DAY = 24
PRODUCT_ID = '-//M & Z Product//Berkeley iCal//EN'


def display(cal):
    return cal.to_ical().replace('\r\n', '\n').strip()


def create_event(uid, dtstart, dtend, location, rule, summary):
    event = Event()
    event['uid'] = uid
    event.add('dtstart', dtstart)
    event.add('dtend', dtend)
    event['location'] = location
    event['summary'] = summary
    event.add('rrule', create_event_rule(rule[0], rule[1], rule[2], rule[3]))
    return event


def create_event_rule(frequency, byday, until, weekdaystarts):
    return {'freq': frequency, 'byday': byday,
            'until': until, 'WKST': weekdaystarts}


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


# To do
def add_name_to_cal(event, name):
    return

def scrap_data():
    soup = bs4.BeautifulSoup(open("Schedule Planner.htm").read().replace('\n', ''), 'html.parser')
    schedule_table_body = soup.find("div", class_="current-schedule")\
                              .find("table", class_="section-detail-grid")\
                              .find("tbody")
    courses = {}
    for tr in schedule_table_body.children:
        if isinstance(tr, bs4.element.Tag):
            status = tr.contents[5].string.strip()
            subject = tr.contents[7].string.strip()
            number = tr.contents[9].string.strip()
            component = tr.contents[11].string.strip()
            # instructor
            instr_div = tr.contents[13].find('div')
            if instr_div:
                instructor = instr_div.string.strip()
            else:
                instructor = "N/A"
            # detail - time and location
            detail_div = tr.contents[15].find('div')
            if detail_div:
                detail = detail_div.string.strip()
            else:
                detail = "N/A"
            m = re.match("^(.*) \- (.*)$", detail)
            time = m.group(1)  # TTh 9:30am - 10:59am
            location = m.group(2)  # Dwinelle 155
            unit = tr.contents[17].string.strip()  # num in string format
            # construct object
            this_course = {"subject": subject, "number": number, "component": component, "instructor": instructor,
                           "time": time, "location": location, "status": status, "unit": unit}
            courses[subject + " " + number + " " + component] = this_course
    return courses

def parse_time(time):
    contents = time.split()
    weekdays = []
    contents_weekdays = contents[0]
    for i in range(len(contents_weekdays)):
        if contents_weekdays[i] == 'T':
            if i < len(contents_weekdays)-1 and contents_weekdays[i+1] == 'h':
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
    dtstart = datetime.datetime(FALL_2016_START_YEAR, FALL_2016_START_MONTH, FALL_2016_START_DAY, 
        t_start_parsed[0], t_start_parsed[1], 0)
    dtend = datetime.datetime(FALL_2016_START_YEAR, FALL_2016_START_MONTH, FALL_2016_START_DAY, 
        t_end_parsed[0], t_end_parsed[1], 0)
    return (dtstart, dtend, weekdays)

def parse_hour_minute(t):
    am_pm = t[1][len(t[1])-2:len(t[1])]
    hour, minutes = round_time(int(t[0]), int(t[1][0:2]))
    if am_pm == "pm" and hour < 12:
        hour += 12
    return (hour, minutes)

def round_time(hour, minutes):
    minutes = (minutes + 1) / 5 * 5
    if minutes == 60:
        hour += 1
        minutes = 0
    return (hour, minutes)

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
    path = os.path.expanduser("~/Desktop/scheduleTEST.ics")
    write_to_file(cal, path)

main()
