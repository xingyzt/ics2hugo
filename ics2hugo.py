import argparse
import icalendar
from urllib.request import urlopen
import re
import codecs
import gdown
import logging
import os

def fetch_ics(url):
    ics = urlopen(url)
    return ics.read()

def parse_ics(ics):
    items = []
    cal = icalendar.Calendar.from_ical(ics)
    for comp in cal.walk():
        if comp.name == 'VEVENT':
            event = {}
            event['uid'] = str(comp.get('uid'))
            event['title'] = str(comp.get('summary', default='untitled event'))
            event['modified'] = comp.get('last-modified').dt
            event['date'] = comp.get('dtstart').dt
            event['text'] = str(comp.get('description', default=''))
            event['attach'] = comp.get('attach', default=list())
            event['location'] = str(comp.get('location', default='unknown'))
            items.append(event)
    return items

def write_hugo(path,items):
    for item in items:
        fid = re.sub(r'@.*', '', item['uid'])

        # fname = re.sub(r'[\s/]+', '-', item['title'])
        # fname = re.sub(r'[^0-9a-zA-Z-]*', '', fname)

        fpath = f'{path}/{fid}.md'.lower()

        # don't update if not modified

        last_modified = -1

        if os.path.isfile(fpath):
            with open(fpath,'r') as mdfile:
                for line in mdfile:
                    match = re.search(r'modified="(.*)"', line)
                    if match:
                        last_modified = match.group(1)
                        break

        if last_modified == str(item["modified"]):
            print('Skipping because up-to-date:', item['title'])
            continue

        print('Updating:', item['title'])

        # upload attachments

        embeds = list()
        for (i, url) in enumerate(item['attach']):
            aid=re.search(r'id=(.*)', url).group(1)
            try:
                gpath = gdown.download(id=aid)
                ext = os.path.splitext(gpath)[1]
                apath = f'{path}/{aid}{ext}'.lower()
                os.rename(gpath, apath)
                embeds.append(f'![{ aid }]({ apath })')
                print('Uploaded:', apath)
            except gdown.exceptions.FileURLRetrievalError:
                logging.exception(f'Failed to download. Check permissions: {url}')

        # upload article

        with open(fpath,'w') as mdfile:
            mdfile.write('+++\n')
            mdfile.write(f'modified="{ item["modified"] }"\n')
            mdfile.write(f'date="{ item["date"] }"\n')
            mdfile.write(f'title="{ item["title"] }"\n')
            mdfile.write('+++\n\n')

            mdfile.write('\n'.join(embeds))
            mdfile.write('\n\n')

            mdfile.write(item['text'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ics2hugo (markdown) conversion tool.')
    parser.add_argument('--url', required=True, help='url to ics calendar.')
    parser.add_argument('--path', required=True ,help='output path of markdown files.')
    args = parser.parse_args()
    ics = fetch_ics(args.url)
    items = parse_ics(ics)
    write_hugo(args.path,items)
