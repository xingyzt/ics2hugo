import argparse
import icalendar
from urllib.request import urlopen
import re
import codecs

def fetch_ics(url):
    ics = urlopen(url)
    return ics.read()

def parse_ics(ics):
    items = []
    cal = icalendar.Calendar.from_ical(ics)
    for comp in cal.walk():
        if comp.name == 'VEVENT':
            event = {}
            print(comp.get('summary'))
            event['title'] = comp.get('summary') or ''
            event['date'] = str(comp.get('dtstart').dt)
            event['text'] = comp.get('description') or ''
            items.append(event)
    return items

def write_hugo(path,items):
    for item in items:
        fname = item['title'] + '-' + item['date'][:10]
        fname = fname.lower()
        fname = re.sub(r'[\s/]+', '-', fname)
        fname = re.sub(r'[^0-9a-zA-Z-]*', '', fname)
        fpath = f'{path}/{fname}.md'
        print(fname)
        with open(fpath,'w') as mdfile:
            mdfile.write('+++\n')
            mdfile.write(f'date = "{ item["date"] }"\n')
            mdfile.write(f'title = "{ item["title"] }"\n')
            mdfile.write('+++\n\n')
            mdfile.write(item['text'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ics2hugo (markdown) conversion tool.')
    parser.add_argument('--url', required=True, help='url to ics calendar.')
    parser.add_argument('--path', required=True ,help='output path of markdown files.')
    args = parser.parse_args()
    ics = fetch_ics(args.url)
    items = parse_ics(ics)
    write_hugo(args.path,items)
