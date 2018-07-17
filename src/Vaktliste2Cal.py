"""
Shows basic usage of the Google Calendar API. Creates a Google Calendar API
service object and outputs a list of the next 10 events on the user's calendar.
"""
from pprint import pprint

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime


calendar_id_familien = '92jabjrjs87tq32dhdh3565aic@group.calendar.google.com'
calendar_id_primary = 'primary'
color_id_familien_magnus = 11
color_id_primary_magnus = 5

# Setup the Calendar API
SCOPES = 'https://www.googleapis.com/auth/calendar'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('calendar', 'v3', http=creds.authorize(Http()))

# Call the Calendar API
now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
print('Getting the upcoming 10 events')
events_result = service.events().list(calendarId=calendar_id_familien, timeMin=now,
                                      maxResults=10, singleEvents=True,
                                      orderBy='startTime').execute()
events = events_result.get('items', [])

if not events:
    print('No upcoming events found.')
for event in events:
    start = event['start'].get('dateTime', event['start'].get('date'))
    print(start, event['summary'], event.get('colorId', 'NO COLOR'), event['id'])

new_event = service.events().insert(calendarId=calendar_id_primary, body={
    'summary': 'Testevent',
    'colorId': color_id_primary_magnus,
    'start': {
        'dateTime': '2018-04-24T16:00:00',
        'timeZone': 'Europe/Oslo'
    },
    'end': {
        'dateTime': '2018-04-24T17:00:00',
        'timeZone': 'Europe/Oslo'
    }
})#.execute()
pprint(new_event)


vaktliste = {
    'Magnus': [
        {
            'date': '2018-04-24',
            'startTime': '18:30:00',
            'endTime': '22:30:00',
            'door': 'A',
            'shiftLeader': True,

            'playStart': '19:30:00',
            'playEnd': '22:10:00',
            'play': 'Spelemann på taket',
            'stage': 'Hovedscenen'
        },
        {
            'date': '2018-04-25',
            'startTime': '18:00:00',
            'endTime': '22:30:00',
            'door': 'Venstre parkett',
            'shiftLeader': True,

            'playStart': '19:00:00',
            'playEnd': '22:10:00',
            'play': 'Meteoren',
            'stage': 'Gamle Scene'
        }
        # etc.
    ]
}
pprint(vaktliste)
