#!/usr/bin/env python

from urllib.parse import quote
import requests
import base64
import json
import dictcom
import utils
from bs4 import BeautifulSoup
from models import File
from utils import dump_json

NAME = 'forvo'
AUDIO_HOST = 'https://audio00.forvo.com/audios/mp3'

first = lambda a: next(iter(a or []), None)


def decode_base64(s):
    return base64.b64decode(s).decode('utf-8')


def unquote(s):
    if s.startswith('\''):
        return s[1:len(s) - 1]
    return s


def parse_fn(src):
    if not src:
        return None
    i = src.find('(')
    j = src.find(')')
    name = src[:i]
    args = [unquote(s) for s in src[i + 1:j].split(',')]
    return {'name': name, 'args': args}


def translate_gender(val):
    val = val.strip()
    if val == '\u0436\u0435\u043d\u0449\u0438\u043d\u0430':
        return 'f'
    if val == '\u043c\u0443\u0436\u0447\u0438\u043d\u0430':
        return 'm'
    return val


def translate_counry(val):
    val = val.strip()
    r = dictcom.translate(val)
    if r is not None and len(r['tran']) > 0:
        return r['tran'][0].lower()
    return val


def parse_from(s):
    if not s:
        return None
    s = s.strip('(').strip(')')
    a = s.split(',')
    if len(a) == 0:
        return None
    result = {'gender': translate_gender(a[0])}
    if len(a) == 2:
        result['country'] = translate_counry(a[1])
    return result


def parse_item(item):
    btn = item.find('span', class_='play')
    if btn is None:
        return None

    fn = parse_fn(btn['onclick'])
    if fn is None or fn['name'] != 'Play':
        return None
    rel = decode_base64(fn['args'][4])
    url = f'{AUDIO_HOST}/{rel}'
    if not url.endswith('.mp3'):
        return None

    result = {'url': url}
    author = item.find('span', class_='ofLink')
    if author and 'data-p2' in author.attrs:
        result['author'] = author.attrs['data-p2']

    from_tag = item.find('span', class_='from')
    if from_tag:
        d = parse_from(from_tag.contents[0])
        if d:
            for k, v in d.items():
                result[k] = v

    return result


def get_data(text, lang='ru'):
    url = f'https://ru.forvo.com/word/{quote(text)}/#{lang}'
    headers = {
        'User-Agent': utils.CHROME_USER_AGENT,
        'Accept': 'text/html',
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, 'html.parser')
    article = soup.find('article', class_='pronunciations')
    if article is None:
        return None
    ul = article.find('ul', class_="show-all-pronunciations")
    if ul is None:
        return None

    li = ul.find_all('li')
    parsed_items = [parse_item(t) for t in li]
    items = [
        t for t in parsed_items if t is not None and utils.url_exists(t['url'])
    ]

    for item in items:
        yield ('audio', File(url=item['url'], region=None))


def main():
    (text, lang) = utils.find_audio_args()
    result = get_data(text, lang)
    print(dump_json(result))


if __name__ == '__main__':
    main()
