from icalendar import Calendar, Event, Timezone, TimezoneStandard, TimezoneDaylight; from dateutil import *
import re, bs4, os, datetime

# return a .ics formatted string
FALL_2016_END = datetime.datetime(2016, 12, 3, 0, 0, 0)


def display(cal):
    return cal.to_ical().replace('\r\n', '\n').strip()


def create_event(uid, dtstart, dtend, location, rule, summary):
    event = Event()
    event['uid'] = uid
    event['dtstart'] = dtstart
    event['dtend'] = dtend
    event['location'] = location
    event['summary'] = summary
    print(location)
    print(summary)
    print(rule)
    event.add('rrule', create_event_rule(rule[0], rule[1], rule[2], rule[3], rule[4]))
    return event


def create_event_rule(frequency, byday, bymonth, until, weekdaystarts):
    return {'freq': frequency, 'byday': byday, 'bymonth': bymonth,
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

def write_to_file(calendar, path):
    f = open(path, "w")
    f.write(calendar.to_ical())
    f.close()

def main():
    cal = Calendar()
    cal.add_component(create_default_timezone())
    uid = 1
    for course, info in scrap_data().iteritems():
        summary = course 
        location = info["location"]
        dtstart = '19701101T020000'
        dtend = '19701101T020000'
        rule = ['weekly', ['tu', 'th'], 3, FALL_2016_END, 'su']
        event = create_event(uid, dtstart, dtend, location, rule, summary)
        cal.add_component(event)
        uid += 1
    cal["X-WR-TIMEZONE"] = "America/Los_Angeles"
    path = os.path.expanduser("~/Desktop/scheduleTEST.ics")
    write_to_file(cal, path)

main()


# TO DO: iteratively add events to calendar
# for ... in events:
#       cal.add_component(createEvent(...))
