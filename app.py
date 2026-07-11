import os
import json
import streamlit as st
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Import modules
from src.news_collector import FMCGNewsCollector
from src.deduplicator import Deduplicator
from src.relevance_filter import RelevenceFilter
from src.credibility_scorer import CredibilityScorer
from src.newsletter_generator import NewsletterGenerator

load_dotenv()

st.set_page_config(page_title="FMCG M&A Intelligence Newsletter", layout="wide")

st.title("📊 FMCG M&A Intelligence Newsletter")
st.markdown("*Automated deal monitoring & newsletter generation*")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    days_back = st.selectbox(
        "Time range", 
        ["any_time", "past_hour", "past_day", "past_week", "past_month", "past_year"],
        index=4  # Default to past_month
    )
    get_api_key = st.text_input("Enter your Api Key: ", type='password')
    min_credibility = st.slider("Minimum credibility score", 30, 80, 50)
    use_llm = st.checkbox("Enable AI Summarization", False, 
                         help="Requires OpenAI API key")
    run_btn = st.button("🔄 Generate Newsletter", type="primary")


# Main area
if run_btn:
    with st.spinner("🔄 Processing..."):
        try:
            # 1. Ingest
            st.write("📥 Fetching articles...")
            collector = FMCGNewsCollector(api_key=os.getenv("NEWS_API_KEY"))
            raw_response = collector.fetch_articles(time_line=days_back)
            
            # Extract articles from response
            raw_articles = raw_response.get('organic', [])
            
            if not raw_articles:
                st.error("❌ No articles found. Please check your API key or try a different time range.")
                st.stop()
            
            st.write(f"✅ Found {len(raw_articles)} raw articles")
            
            # 2. Deduplicate
            st.write("🔄 Deduplicating...")
            deduplicator = Deduplicator()
            deduped = deduplicator.find_duplicates(raw_articles)
            st.write(f"✅ After deduplication: {len(deduped)} articles")
            
            # 3. Filter relevance
            st.write("🎯 Filtering for relevance...")
            filter_ = RelevenceFilter()
            relevant = [a for a in deduped if filter_.is_relevant(a)]
            st.write(f"✅ Relevant articles: {len(relevant)}")
            
            # 4. Score credibility
            st.write("⭐ Scoring credibility...")
            scorer = CredibilityScorer()
            scored = []
            for article in relevant:
                result = scorer.score_article(article)
                if result['score'] >= min_credibility:
                    article['credibility_score'] = result['score']
                    article['credibility_breakdown'] = result['breakdown']
                    scored.append(article)
            st.write(f"✅ High-credibility articles: {len(scored)}")
            
            # 5. Generate newsletter
            st.write("📰 Generating newsletter...")
            generator = NewsletterGenerator(use_llm=use_llm, api_key=get_api_key)
            newsletter = generator.generate(scored)
            
            # Display results
            st.success(f"✅ Processed {len(raw_articles)} articles → {len(scored)} high-quality deals")
            
            # Show metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Raw Articles", len(raw_articles))
            col2.metric("After Dedupe", len(deduped))
            col3.metric("Relevant Deals", len(relevant))
            col4.metric("Final Selected", len(scored))
            
            # Display newsletter sections
            st.header("📰 Newsletter Preview")
            
            # Executive Summary
            st.subheader("📝 Executive Summary")
            st.info(newsletter.get('summary', 'No summary available'))
            
            # Top Deals
            st.subheader("💰 Top Deals")
            if newsletter.get('deals'):
                for deal in newsletter['deals']:
                    with st.expander(f"{deal.get('acquirer', 'Unknown')} → {deal.get('target', 'Unknown')} ({deal.get('amount', 'Undisclosed')})"):
                        st.write(f"**Amount:** {deal.get('amount', 'Undisclosed')}")
                        if deal.get('credibility'):
                            st.write(f"**Credibility Score:** {deal.get('credibility')}/100")
                        st.write(f"**Summary:** {deal.get('summary', 'No summary available')}")
            else:
                st.warning("No deals found matching the criteria")
            
            # Trends
            if newsletter.get('trends'):
                st.subheader("📈 Emerging Trends")
                for trend in newsletter['trends']:
                    st.markdown(f"• {trend}")
            
            # Metrics
            st.subheader("📊 Deal Metrics")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Deals", len(newsletter.get('deals', [])))
            col2.metric("Total Articles", newsletter.get('total_articles', 0))
            col3.metric("Date", newsletter.get('date', ''))
            
            # Download buttons
            st.subheader("📥 Download Options")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                json_data = json.dumps(newsletter, indent=2)
                st.download_button(
                    label="📥 Download JSON",
                    data=json_data,
                    file_name=f"newsletter_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
            
            with col2:
                markdown_content = generator.to_markdown(newsletter)
                st.download_button(
                    label="📥 Download Markdown",
                    data=markdown_content,
                    file_name=f"newsletter_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown"
                )
            
            with col3:
                if newsletter.get('deals'):
                    df = pd.DataFrame(newsletter['deals'])
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"deals_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            
            # Raw data expander
            with st.expander("📊 Raw Data"):
                st.json(newsletter)
            
            # Show credibility breakdown
            with st.expander("🔍 Credibility Breakdown"):
                for article in scored:
                    st.write(f"**{article.get('title', 'Unknown')}**")
                    st.write(f"Score: {article.get('credibility_score', 0)}/100")
                    st.write("Breakdown:")
                    for reason in article.get('credibility_breakdown', []):
                        st.write(f"  • {reason}")
                    st.divider()
                    
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.write("Please check your API keys and try again.")

# Instructions
with st.expander("ℹ️ How to use"):
    st.markdown("""
    1. **Configure** - Set time range and minimum credibility score
    2. **Enable AI** - Toggle AI summarization (requires OpenAI API key)
    3. **Generate** - Click 'Generate Newsletter' button
    4. **Review** - View executive summary, top deals, and trends
    5. **Export** - Download in JSON, Markdown, or CSV format
    
    **Pipeline:** Ingestion → Deduplication → Relevance Filtering → Credibility Scoring → Newsletter Generation
    """)

# Footer
st.divider()
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")