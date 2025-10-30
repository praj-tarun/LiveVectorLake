"""Wikipedia connector for streaming article ingestion"""
import requests
from typing import List, Dict, Optional
from datetime import datetime
import time

class WikipediaConnector:
    """Fetch Wikipedia articles via API"""
    
    def __init__(self, language: str = "en"):
        self.language = language
        self.base_url = f"https://{language}.wikipedia.org/w/api.php"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LiveVectorLake/1.0 (Educational Research Project)'
        })
    
    def search_articles(self, query: str, limit: int = 10) -> List[str]:
        """Search for article titles matching query
        
        Args:
            query: Search term
            limit: Max number of results
            
        Returns:
            List of article titles
        """
        params = {
            "action": "opensearch",
            "search": query,
            "limit": limit,
            "format": "json"
        }
        
        response = self.session.get(self.base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data[1] if len(data) > 1 else []
    
    def get_article_content(self, title: str) -> Optional[Dict]:
        """Fetch article content by title
        
        Args:
            title: Article title
            
        Returns:
            Dictionary with article data or None if not found
        """
        params = {
            "action": "query",
            "titles": title,
            "prop": "extracts|info",
            "explaintext": True,
            "inprop": "url",
            "format": "json"
        }
        
        response = self.session.get(self.base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        
        if not pages:
            return None
        
        page_id = list(pages.keys())[0]
        if page_id == "-1":
            return None
        
        page = pages[page_id]
        
        return {
            "doc_id": f"wikipedia_{page_id}",
            "title": page.get("title", ""),
            "content": page.get("extract", ""),
            "url": page.get("fullurl", ""),
            "source": "wikipedia",
            "fetched_at": datetime.utcnow().isoformat() + "Z"
        }
    
    def fetch_articles_by_topic(self, topic: str, count: int = 5) -> List[Dict]:
        """Fetch multiple articles on a topic
        
        Args:
            topic: Topic to search for
            count: Number of articles to fetch
            
        Returns:
            List of article dictionaries
        """
        titles = self.search_articles(topic, limit=count)
        articles = []
        
        for title in titles:
            article = self.get_article_content(title)
            if article and article["content"]:
                articles.append(article)
            time.sleep(0.1)  # Rate limiting
        
        return articles
    
    def stream_articles(self, topics: List[str], interval: int = 300) -> Dict:
        """Simulate streaming by fetching articles periodically
        
        Args:
            topics: List of topics to fetch
            interval: Seconds between fetches (default 5 min)
            
        Yields:
            Article dictionaries
        """
        while True:
            for topic in topics:
                articles = self.fetch_articles_by_topic(topic, count=3)
                for article in articles:
                    yield article
            
            time.sleep(interval)
