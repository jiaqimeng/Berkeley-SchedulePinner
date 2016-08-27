from icalendar import Calendar, Event, Timezone, TimezoneStandard, TimezoneDaylight

# return a .ics formatted string

def display(cal):
	return cal.to_ical().replace('\r\n', '\n').strip()

def createEvent(uid, dtstart, dtend, location, rule, summary):
	event = Event()
	event['uid'] = uid
	event['dtstart'] = dtstart
	event['dtend'] = dtend
	event['location'] = location
	event['summary'] = summary
	event['rrule'] = createEventRule(rule)
	return event

def createEventRule(frequency, byday, bymonth, byyear, until, weekdaystarts):
	return {'freq': frequency, 'byday': byday, 'bymonth': bymonth,
	 'byyear': byyear, 'until': until, 'weekdaystarts': weekdaystarts}

def createDefaultTimezone():
	timezone = Timezone()
	timezone['TZID'] = 'America/Los_Angeles'

	timezoneStandard = TimezoneStandard()
	timezoneStandard['dtstart'] = '19701101T020000'
	timezoneStandard['rrule'] = {'freq': 'yearly', 'bymonth': 11, 'byday': '1su'}
	timezoneStandard['tzname'] = 'PST'
	timezoneStandard['tzoffsetfrom'] = '-0700'
	timezoneStandard['tzoffsetto'] = '-0800'

	timezoneDaylight = TimezoneDaylight()
	timezoneDaylight['dtstart'] = '19700308T020000'
	timezoneDaylight['rrule'] = {'freq': 'yearly', 'bymonth': 3, 'byday': '2SU'}
	timezoneDaylight['dtstart']
	timezoneDaylight['TZNAME'] = 'PDT'
	timezoneDaylight['tzoffsetfrom'] = '-0800'
	timezoneDaylight['tzoffsetto'] = '-0700'

	timezone.add_component(timezoneStandard)
	timezone.add_component(timezoneDaylight)
	timezone['X-LIC-LOCATION'] = 'America/Los_Angeles'
	return timezone

# To do
def addNameToCal(event, name):
	return	

def main():
	cal = Calendar()
	cal.add_component(createDefaultTimezone())
	# TO DO: iteratively add events to calendar
	# for ... in events:
#		cal.add_component(createEvent(...))

