# -*- coding: utf-8 -*-
###############################################################################
#                           "A BEER-WARE LICENSE"                             #
# ----------------------------------------------------------------------------#
# Feel free to do whatever you wish with this file. Since we most likey will  #
# never meet, buy a stranger a beer. Give credit to ALL named, unnamed, past, #
# present and future dev's of this & files like this. -Share the Knowledge!   #
###############################################################################

# Addon Name: Fuzzy Britches v4 Module
# Addon id: script.module.fuzzybritches_v4
# Addon Provider: The Papaw

'''
Included with the Fuzzy Britches Add-on
'''

import re

try: from urlparse import parse_qs, urljoin
except ImportError: from urllib.parse import parse_qs, urljoin
try: from urllib import urlencode, quote_plus, quote
except ImportError: from urllib.parse import urlencode, quote_plus, quote

from six import ensure_text

from resources.lib.modules import debrid
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import workers
from resources.lib.modules import source_utils




class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['zooqle.com']
        self.base_link = 'https://zooqle.com'
        self.search = 'https://zooqle.com/search?q={0}+%2Blang%3Aen'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urlencode(url)
            return url
        except Exception:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urlencode(url)
            return url
        except Exception:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url is None: return

            url = parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urlencode(url)
            return url
        except Exception:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            self._sources = []
            if url is None:
                return self._sources

            if debrid.status() is False:
                raise Exception()

            data = parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            self.title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            self.hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            query = '%s S%02dE%02d' % (
            data['tvshowtitle'], int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else '%s %s' % (
            data['title'], data['year'])
            query = re.sub(r'(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)
            url = self.search.format(quote(query))

            self.hostDict = hostDict + hostprDict
            headers = {'User-Agent': client.agent()}
            r = client.request(url, headers=headers)
            posts = client.parseDOM(r, 'table')
            posts = client.parseDOM(posts, 'tr')
            threads = []
            for i in posts:
                threads.append(workers.Thread(self._get_items, i))
            [i.start() for i in threads]
            [i.join() for i in threads]

            return self._sources
        except Exception:
            return self._sources

    def _get_items(self, _html):
        try:
            url = client.parseDOM(_html, 'a', attrs={'title': 'Magnet link'}, ret='href')[0]
            name = client.parseDOM(_html, 'a')[0]
            name = ensure_text(name)
            name = re.sub('<.+?>', '', name)
            t = name.split(self.hdlr)[0]

            try:
                y = re.findall(r'[\.|\(|\[|\s|\_|\-](S\d+E\d+|S\d+)[\.|\)|\]|\s|\_|\-]', name, re.I)[-1].upper()
            except Exception:
                y = re.findall(r'[\.|\(|\[|\s\_|\-](\d{4})[\.|\)|\]|\s\_|\-]', name, re.I)[-1].upper()

            try:
                size = re.findall(r'((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GiB|MiB|GB|MB))', _html)[0]
                div = 1 if size.endswith('GB') else 1024
                size = float(re.sub('[^0-9|/.|/,]', '', size.replace(',', '.'))) / div
                size = '%.2f GB' % size
            except Exception:
                size = '0'

            quality, info = source_utils.get_release_quality(name, name)
            info.append(size)
            info = ' | '.join(info)

            if cleantitle.get(re.sub('(|)', '', t)) == cleantitle.get(self.title):
                if y == self.hdlr:
                    self._sources.append({'source': 'torrent', 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True})
        except Exception:
            pass

    def resolve(self, url):
        return url
