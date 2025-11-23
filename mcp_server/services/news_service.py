import requests
import xml.etree.ElementTree as ET
from typing import List, Dict
import time
from datetime import datetime

class NewsService:
    def __init__(self):
        # Google News - Technology Topic RSS
        self.feeds = [
            "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen"
        ]
        self.cache = []
        self.last_fetch = 0
        self.cache_duration = 60  # Cache for 1 minute (matches frontend refresh)

    def fetch_news(self) -> List[Dict]:
        current_time = time.time()
        
        # Return cached news if valid
        if self.cache and (current_time - self.last_fetch < self.cache_duration):
            return self.cache

        news_items = []
        
        for feed_url in self.feeds:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(feed_url, headers=headers, timeout=5)
                if response.status_code == 200:
                    root = ET.fromstring(response.content)
                    
                    # Handle different RSS formats
                    # Try RSS 2.0 first
                    channel = root.find('channel')
                    items = []
                    if channel is not None:
                        items = channel.findall('item')
                    else:
                        # Try Atom (root is feed, children are entries)
                        # Atom uses namespaces, so we might need to handle that or just search by tag name ignoring namespace
                        # Simple hack: iterate all children and check tag
                        items = [child for child in root if child.tag.endswith('entry')]
                        if not items:
                             # Fallback: find all 'item' or 'entry' anywhere
                            items = root.findall('.//item') + root.findall('.//{http://www.w3.org/2005/Atom}entry')

                    for item in items[:3]: # Get top 3
                        try:
                            # Helper to find text in child tags (handling namespaces roughly)
                            def get_text(elem, tag_name):
                                found = elem.find(tag_name)
                                if found is not None: return found.text
                                # Try with namespace
                                for child in elem:
                                    if child.tag.endswith(tag_name):
                                        return child.text
                                return ""

                            title = get_text(item, 'title')
                            link = get_text(item, 'link')
                            # Atom links are often attributes <link href="...">
                            if not link and item.find("{http://www.w3.org/2005/Atom}link") is not None:
                                link = item.find("{http://www.w3.org/2005/Atom}link").get('href')
                            
                            pub_date = get_text(item, 'pubDate') or get_text(item, 'updated') or ""
                            
                            if title and link:
                                news_items.append({
                                    "title": title,
                                    "url": link,
                                    "source": self._get_source_name(feed_url),
                                    "time": pub_date
                                })
                        except Exception as e:
                            print(f"Error parsing item in {feed_url}: {e}")
                            continue
            except Exception as e:
                print(f"Error fetching feed {feed_url}: {e}")
                continue
        
        # Sort by time (simple shuffle for now as date parsing is complex across feeds)
        # In a real app, we'd parse datetime objects. 
        # For now, we'll just return the mixed list.
        
        self.cache = news_items
        self.last_fetch = current_time
        return news_items

    def _get_source_name(self, url: str) -> str:
        if "google" in url: return "Google News"
        if "techcrunch" in url: return "TechCrunch"
        if "theverge" in url: return "The Verge"
        if "hnrss" in url: return "Hacker News"
        return "Tech News"

news_service = NewsService()

def get_latest_news():
    return news_service.fetch_news()
