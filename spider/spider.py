from bs4 import BeautifulSoup, SoupStrainer
import tldextract
import json
import re
from urllib.parse import urlparse
import requests


ARCHIVE_WEB_URL = 'http://web.archive.org/web'
ARCHIVE_CDX_URL = 'http://web.archive.org/cdx/search/cdx'

MAX_EXTRACTION_LEVEL = 5


class Spider:
    def __init__(self, extraction_level, collapse):
        self.extract = tldextract.TLDExtract()
        self.extraction_level = min(extraction_level, MAX_EXTRACTION_LEVEL)
        self.collapse = collapse

    def crawl_for_links(self, url):
        """ Entry point to start crawling URL """
        pass_urls = {}
        found_links = []

        p = urlparse('http://' + url[42:])
        page = p.path
        self.extract_links_from_url(url[:42] + urlparse([p.scheme, p.netloc, '', '', '', '']),
                                    page,
                                    0,
                                    pass_urls,
                                    found_links)

        return found_links

    def get_content(self, url):
        """ Returns the HTML content of a specific URL """
        website = requests.get(url)
        content_type = website.headers['Content-Type'].lower()

        if content_type.startswith('text/html'):
            return website.content
        else:
            return None

    def extract_links_from_url(self, base_url, page, level, pass_urls, found_links):
        """
        The crawler recursive function
        ------------------------------

        This function reads single HTML page and extract all href links.
        Each internal link is process in the same way (till the define extraction level).
        The external links are collected and returned at the end of the crawling process.
        """
        if level > self.extraction_level:
            return

        base_ext = self.extract(base_url[42:])

        # replace spaces to %20
        page = page.replace(' ', '%20')

        if not base_url.endswith('/'):
            base_url += '/'
        current_url = base_url + page
        if pass_urls.has_key(current_url):
            return

        pass_urls[current_url] = 0

        html = self.get_content(current_url)
        if html is None:
            return

        soup = BeautifulSoup(html, 'html.parser', parse_only=SoupStrainer("a"))
        for tag in soup.findAll('a', href=True):
            href = tag['href'].lower()
            href = re.sub(r'(?:http:\/\/web\.archive\.org)?\/web\/\d{14}\/', '', href)
            ext_link = self.extract(href)
            if ext_link.domain != '' and ext_link.subdomain != '' and ext_link.suffix != '' and base_ext.domain != ext_link.domain and ext_link.domain != 'localhost':
                found_links.append('%s.%s.%s' % (ext_link.subdomain, ext_link.domain, ext_link.suffix))
            else:
                path = urlparse(href).path
                if path.startswith('/'):
                    path = path[1:]
                    self.extract_links_from_url(base_url, path, level + 1, pass_urls, found_links)

    def get_snapshots_timestamp_from_cdx(self, url):
        """ Returns list of existing snapshots timestamp in the IA for specific URL """
        cdx_result = requests.get(ARCHIVE_CDX_URL, params={'url': url,
                                                           'limit': 1000,
                                                           'output': 'json',
                                                           'collapse': 'timestamp:%d' % self.collapse})
        snapshots_timestamp = []

        cdx_result = json.loads(cdx_result.content)
        if len(cdx_result) > 0:
            cdx_result.pop(0)  # remove header row
            for item in cdx_result:
                snapshots_timestamp.append(item[1])

        return snapshots_timestamp

    def crawl(self, url):
        """ """
        external_links = {}

        snapshots_timestamp = self.get_snapshots_timestamp_from_cdx(url)
        if len(snapshots_timestamp) > 0:
            for ts in snapshots_timestamp:
                try:
                    found = self.crawl_for_links('%s/%s/%s' % (ARCHIVE_WEB_URL,
                                                               ts,
                                                               url))
                    if len(found) > 0:
                        external_links[ts] = list(set(found))
                except Exception as ex:
                    pass

        return external_links

