import datetime
import requests
import time
import json
from dateutil import parser
from cal_setup import get_calendar_service

def postEvent(event, webhook_url):
    event_time = time.mktime(parser.parse(event['start'].get('dateTime')).timetuple())
    data = { "content":"<@&948436677569962016>\n"+ event['summary'] + " at <t:" + str(int(event_time)) + "> <t:" + str(int(event_time)) + ":R>" }
    r = requests.post(webhook_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
    return

def postEventStart(event, webhook_url):
    data = { "content":"<@&948436677569962016>\n" + event['summary'] + " starts NOW!" }
    r = requests.post(webhook_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
    return

def main():
    print('Initializing config.')
    f = open('config.json')
    config = json.load(f)
    webhook_url = config['webhook_url']
    currentPostedID = config['currentPostedID']
    runningEventID = config['runningEventID']
    f.close()
    print('Config initialized.')

    while True:
        service = get_calendar_service()
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        print('Checking Calendar...')
        events_result = service.events().list(
            calendarId='u4e26gcuqtna00hcmu5tpancfc@group.calendar.google.com', timeMin=now,
            maxResults=1, singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        for event in events:
            event_time = time.mktime(parser.parse(event['start'].get('dateTime')).timetuple())
            if event['id'] != currentPostedID:
                print("Posting event.")
                postEvent(event, webhook_url)
                currentPostedID = event['id']
                config['currentPostedID'] = currentPostedID
                with open('config.json', 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=4)
            elif event_time < time.mktime(datetime.datetime.now().timetuple()):
                if event['id'] != runningEventID:
                    print("Posting Event Start.")
                    postEventStart(event, webhook_url)
                    runningEventID = event['id']
                    config['runningEventID'] = runningEventID
                    with open('config.json', 'w', encoding='utf-8') as f:
                        json.dump(config, f, ensure_ascii=False, indent=4)
        time.sleep(60)

if __name__ == '__main__':
    main()
