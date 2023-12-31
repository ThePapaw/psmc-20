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

from six import ensure_text

import json, time

from resources.lib.modules import cleantitle, client, debrid, source_utils, log_utils, control, cfscrape

try: from urlparse import parse_qs
except ImportError: from urllib.parse import parse_qs
try: from urllib import urlencode, quote_plus
except ImportError: from urllib.parse import urlencode, quote_plus


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.tvsearch = 'https://torrentapi.org/pubapi_v2.php?app_id=thecrew&token={0}&mode=search&search_string={1}&{2}'
        self.msearch = 'https://torrentapi.org/pubapi_v2.php?app_id=thecrew&token={0}&mode=search&search_imdb={1}&{2}'
        self.token = 'https://torrentapi.org/pubapi_v2.php?app_id=thecrew&get_token=get_token'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urlencode(url)
            return url
        except BaseException:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urlencode(url)
            return url
        except BaseException:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url is None: return
            url = parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urlencode(url)
            return url
        except BaseException:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            scraper = cfscrape.create_scraper()
            if url is None: return sources
            if debrid.status() is False: return sources
            data = parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            title = cleantitle.get_query(title)
            query = '%s S%02dE%02d' % (title, int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else '%s' % data['imdb']
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)
            token = scraper.get(self.token).content
            token = json.loads(token)["token"]
            if 'tvshowtitle' in data:
                search_link = self.tvsearch.format(token, quote_plus(query), 'format=json_extended')
            else:
                search_link = self.msearch.format(token, data['imdb'], 'format=json_extended')
            control.sleep(250)
            rjson = scraper.get(search_link).content
            rjson = ensure_text(rjson, errors='ignore')
            files = json.loads(rjson)['torrent_results']
            for file in files:
                name = file["title"]
                quality, info = source_utils.get_release_quality(name, name)
                size = source_utils.convert_size(file["size"])
                info.append(size)
                info = ' | '.join(info)
                url = file["download"]
                url = url.split('&tr')[0]
                sources.append({'source': 'Torrent', 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True})
            return sources
        except:
            log_utils.log('torapi - Exception', 1)
            return sources

    def resolve(self, url):
        return url
