import bs4
import re

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

print(courses)