"""Test Wikipedia connector"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from sources.wikipedia_connector import WikipediaConnector

def test_search():
    """Test article search"""
    print("\n" + "="*60)
    print("TEST: Wikipedia Search")
    print("="*60)
    
    connector = WikipediaConnector()
    titles = connector.search_articles("artificial intelligence", limit=5)
    
    print(f"\nFound {len(titles)} articles:")
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")
    
    assert len(titles) > 0, "Should find articles"
    print("\nTest PASSED")

def test_fetch_article():
    """Test fetching article content"""
    print("\n" + "="*60)
    print("TEST: Fetch Article Content")
    print("="*60)
    
    connector = WikipediaConnector()
    article = connector.get_article_content("Artificial intelligence")
    
    if article:
        print(f"\nTitle: {article['title']}")
        print(f"Doc ID: {article['doc_id']}")
        print(f"Source: {article['source']}")
        print(f"Content length: {len(article['content'])} chars")
        print(f"Content preview: {article['content'][:200]}...")
        
        assert article['content'], "Should have content"
        assert article['source'] == 'wikipedia', "Source should be wikipedia"
        print("\nTest PASSED")
    else:
        print("\nTest FAILED: Article not found")

def test_fetch_by_topic():
    """Test fetching multiple articles by topic"""
    print("\n" + "="*60)
    print("TEST: Fetch Articles by Topic")
    print("="*60)
    
    connector = WikipediaConnector()
    articles = connector.fetch_articles_by_topic("machine learning", count=3)
    
    print(f"\nFetched {len(articles)} articles:")
    for article in articles:
        print(f"- {article['title']} ({len(article['content'])} chars)")
    
    assert len(articles) > 0, "Should fetch articles"
    print("\nTest PASSED")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("WIKIPEDIA CONNECTOR TESTS")
    print("="*60)
    
    tests_passed = 0
    tests_total = 3
    
    try:
        test_search()
        tests_passed += 1
    except Exception as e:
        print(f"\nSearch test FAILED: {e}")
    
    try:
        test_fetch_article()
        tests_passed += 1
    except Exception as e:
        print(f"\nFetch test FAILED: {e}")
    
    try:
        test_fetch_by_topic()
        tests_passed += 1
    except Exception as e:
        print(f"\nTopic test FAILED: {e}")
    
    print("\n" + "="*60)
    print(f"TESTS COMPLETED: {tests_passed}/{tests_total} passed")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
