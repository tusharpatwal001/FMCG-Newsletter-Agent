# test_pipeline.py - Test each component

import os
from dotenv import load_dotenv
from src.news_collector import FMCGNewsCollector
from src.deduplicator import Deduplicator
from src.relevance_filter import RelevenceFilter
from src.credibility_scorer import CredibilityScorer
from src.newsletter_generator import NewsletterGenerator

load_dotenv()

def test_pipeline():
    print("=" * 50)
    print("TESTING FMCG NEWSLETTER PIPELINE")
    print("=" * 50)
    
    # 1. Test Collector
    print("\n1. Testing News Collector...")
    collector = FMCGNewsCollector(api_key=os.getenv("NEWS_API_KEY"), query=input("Enter the Query: "))
    response = collector.fetch_articles("past_month")
    articles = response.get('organic', [])
    print(f"   ✅ Found {len(articles)} articles")
    
    if not articles:
        print("   ❌ No articles found. Check API key.")
        return
    
    # Show first article structure
    print(f"   Sample article keys: {list(articles[0].keys())}")
    
    # 2. Test Deduplicator
    print("\n2. Testing Deduplicator...")
    deduper = Deduplicator()
    deduped = deduper.find_duplicates(articles)
    print(f"   ✅ After dedupe: {len(deduped)} articles")
    
    # 3. Test Relevance Filter
    print("\n3. Testing Relevance Filter...")
    filter_ = RelevenceFilter()
    relevant = [a for a in deduped if filter_.is_relevant(a)]
    print(f"   ✅ Relevant: {len(relevant)} articles")
    
    if relevant:
        print(f"   Sample relevant: {relevant[0].get('title', 'N/A')[:100]}")
    
    # 4. Test Credibility Scorer
    print("\n4. Testing Credibility Scorer...")
    scorer = CredibilityScorer()
    scored = []
    for article in relevant[:5]:
        result = scorer.score_article(article)
        if result['score'] >= 50:
            article['credibility_score'] = result['score']
            scored.append(article)
            print(f"   ✅ {article.get('title', '')[:50]}... Score: {result['score']}")
    
    # 5. Test Newsletter Generator
    print("\n5. Testing Newsletter Generator...")
    generator = NewsletterGenerator(use_llm=True, api_key=os.getenv("GEMINI_API_KEY"))
    newsletter = generator.generate(scored)
    print("   ✅ Generated newsletter")
    print(f"   Summary: {newsletter.get('summary', 'N/A')}")
    print(f"   Deals found: {len(newsletter.get('deals', []))}")
    
    # Show deals
    for d in newsletter.get('deals', []):
        print(f"   - {d.get('acquirer', '?')} → {d.get('target', '?')} ({d.get('amount', '?')})")
    
    print("\n" + "=" * 50)
    print("✅ PIPELINE TEST COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    test_pipeline()