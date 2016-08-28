from icalendar import Calendar, Event, Timezone, TimezoneStandard, TimezoneDaylight


# return a .ics formatted string


def display(cal):
    return cal.to_ical().replace('\r\n', '\n').strip()


def create_event(uid, dtstart, dtend, location, rule, summary):
    event = Event()
    event['uid'] = uid
    event['dtstart'] = dtstart
    event['dtend'] = dtend
    event['location'] = location
    event['summary'] = summary
    event['rrule'] = create_event_rule(rule)
    return event


def create_event_rule(frequency, byday, bymonth, byyear, until, weekdaystarts):
    return {'freq': frequency, 'byday': byday, 'bymonth': bymonth,
            'byyear': byyear, 'until': until, 'weekdaystarts': weekdaystarts}


def create_default_timezone():
    timezone = Timezone()
    timezone['TZID'] = 'America/Los_Angeles'

    timezone_standard = TimezoneStandard()
    timezone_standard['dtstart'] = '19701101T020000'
    timezone_standard['rrule'] = {'freq': 'yearly', 'bymonth': 11, 'byday': '1su'}
    timezone_standard['tzname'] = 'PST'
    timezone_standard['tzoffsetfrom'] = '-0700'
    timezone_standard['tzoffsetto'] = '-0800'

    timezone_daylight = TimezoneDaylight()
    timezone_daylight['dtstart'] = '19700308T020000'
    timezone_daylight['rrule'] = {'freq': 'yearly', 'bymonth': 3, 'byday': '2SU'}
    timezone_daylight['dtstart']
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


def main():
    cal = Calendar()
    cal.add_component(create_default_timezone())

# TO DO: iteratively add events to calendar
# for ... in events:
#       cal.add_component(createEvent(...))
