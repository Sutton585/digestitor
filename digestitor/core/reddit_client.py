
import json
import sys
from urllib import request, error
import xml.etree.ElementTree as ET
from datetime import datetime

class RedditClient:
    HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    def get_posts_from_rss(self, rss_url, post_limit_per_feed):
        print(f"Fetching RSS feed: {rss_url}")
        try:
            req = request.Request(rss_url, headers=self.HEADERS)
            with request.urlopen(req) as response:
                xml_data = response.read()
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                root = ET.fromstring(xml_data)
                posts = []
                for i, entry in enumerate(root.findall('atom:entry', ns)):
                    if i >= post_limit_per_feed: break
                    id_tag, link_tag, updated_tag = entry.find('atom:id', ns), entry.find('atom:link', ns), entry.find('atom:updated', ns)
                    if all((id_tag is not None, link_tag is not None, updated_tag is not None)):
                        try:
                            post_date = datetime.fromisoformat(updated_tag.text.replace('Z', '+00:00'))
                            posts.append((id_tag.text.split('_')[-1], link_tag.get('href'), post_date))
                        except ValueError: continue
                return posts
        except Exception as e:
            print(f"Error fetching or parsing RSS for {rss_url}: {e}", file=sys.stderr)
            return []

    def fetch_json_from_url(self, json_url):
        print(f"Fetching JSON from: {json_url}")
        try:
            req = request.Request(json_url, headers=self.HEADERS)
            with request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"Error fetching JSON for {json_url}: {e}", file=sys.stderr)
            return None
