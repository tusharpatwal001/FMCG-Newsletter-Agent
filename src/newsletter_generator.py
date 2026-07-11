import os
import re
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import SecretStr
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# api_key = os.getenv("OPEN_API_KEY")

class NewsletterGenerator:
    """Newsletter generator with optional LangChain"""
    
    def __init__(self, use_llm: bool, api_key: str):
        self.use_llm = use_llm
        self.api_key = SecretStr(api_key)
        if use_llm:
            try:
                self.llm = ChatOpenAI(
                    model="gpt-5-nano", 
                    temperature=0.3,
                    api_key=self.api_key
                )
                self.prompt = ChatPromptTemplate.from_template(
                    "Summarize these FMCG deals in 2 sentences: {deals}"
                )
                self.chain = self.prompt | self.llm
            except Exception as e:
                print(f"LLM initialization error: {e}")
                self.use_llm = False
        else:
            self.use_llm = False
    
    def generate(self, articles: List[Dict]) -> Dict:
        """Generate newsletter from articles"""
        if not articles:
            return {
                'title': 'FMCG M&A Briefing',
                'date': datetime.now().strftime('%B %d, %Y'),
                'summary': 'No deals found',
                'deals': [],
                'trends': ['No trends identified'],
                'total_articles': 0
            }
        
        # Extract deals
        deals = []
        for a in articles[:10]:
            text = a.get('title', '') + ' ' + a.get('snippet', '')
            # Check if it's a deal article
            if any(w in text.lower() for w in ['acquire', 'buyout', 'stake', 'merger', 'acquisition']):
                deal = self._parse_deal(a)  # Pass full article
                if deal:
                    deals.append(deal)
        
        # Generate summary
        summary = self._summary(deals) if deals else "No FMCG deals found"
        
        # Extract trends from articles
        trends = []
        for a in articles[:5]:
            title = a.get('title', '')
            if any(w in title.lower() for w in ['trend', 'growth', 'shift', 'surge', 'consolidation']):
                trends.append(title)
        
        return {
            'title': 'FMCG M&A Briefing',
            'date': datetime.now().strftime('%B %d, %Y'),
            'summary': summary,
            'deals': deals[:5],
            'trends': trends[:3] if trends else ['Increased M&A activity in FMCG sector'],
            'total_articles': len(articles)
        }
    
    def _parse_deal(self, article: Dict) -> Optional[Dict]:
        """Extract deal info from article"""
        text = article.get('title', '') + ' ' + article.get('snippet', '')
        
        # Acquirer - company before acquires/buys
        acquirer_patterns = [
            r'([A-Z][a-zA-Z\s]+?)\s+(?:acquires|buys|purchases|to acquire)',
            r'([A-Z][a-zA-Z\s]+?)\s+to\s+buy',
            r'([A-Z][a-zA-Z\s]+?)\s+announces\s+acquisition'
        ]
        
        acquirer = None
        for pattern in acquirer_patterns:
            match = re.search(pattern, text)
            if match:
                acquirer = match.group(1).strip()
                break
        
        # Target - company after acquires/buys
        target_patterns = [
            r'(?:acquires|buys|purchases|to acquire)\s+([A-Z][a-zA-Z\s]+?)(?:\s+for|\s+in|\s+at|\s+$)',
            r'stake\s+in\s+([A-Z][a-zA-Z\s]+?)(?:\s+for|\s+in|\s+$)',
            r'acquisition\s+of\s+([A-Z][a-zA-Z\s]+?)(?:\s+for|\s+in|\s+$)'
        ]
        
        target = None
        for pattern in target_patterns:
            match = re.search(pattern, text)
            if match:
                target = match.group(1).strip()
                break
        
        # Amount
        amount_patterns = [
            r'Rs\s*([\d,]+)\s*(crore|crores)',
            r'Rs\s*([\d,]+)\s*(million|billion)',
            r'\$\s*([\d,]+)\s*(million|billion)',
            r'([\d,]+)\s*(crore|crores)',
            r'([\d,]+)\s*million',
            r'([\d,]+)\s*billion'
        ]
        
        amount = None
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    amount = f"{match.group(1)} {match.group(2)}"
                else:
                    amount = match.group(1)
                break
        
        if not acquirer or not target:
            return None
        
        # Get credibility score
        credibility = article.get('credibility_score', 70)
        
        return {
            'acquirer': acquirer[:50],  # Limit length
            'target': target[:50],
            'amount': f"Rs {amount}" if amount and not amount.startswith(('Rs', '$', 'USD')) else (amount or 'Undisclosed'),
            'credibility': credibility,
            'summary': article.get('title', '')[:150]
        }
    
    def _summary(self, deals: List[Dict]) -> str:
        """Generate summary with optional LLM"""
        if self.use_llm and deals and hasattr(self, 'chain'):
            try:
                deals_text = "\n".join([f"- {d['acquirer']} → {d['target']} ({d['amount']})" 
                                       for d in deals[:3]])
                result = self.chain.invoke({"deals": deals_text})
                return result.content.strip()
            except Exception as e:
                print(f"LLM summary error: {e}")
        
        # Rule-based summary
        total = len(deals)
        disclosed = len([d for d in deals if d['amount'] != 'Undisclosed'])
        
        if total == 0:
            return "No FMCG deals found in the recent period."
        
        # Get top categories
        categories = []
        for d in deals:
            text = d.get('summary', '')
            if 'beauty' in text.lower() or 'personal care' in text.lower():
                categories.append('beauty')
            elif 'food' in text.lower() or 'snack' in text.lower():
                categories.append('food')
            elif 'nutrition' in text.lower() or 'health' in text.lower():
                categories.append('nutrition')
        
        top_cat = max(set(categories), key=categories.count) if categories else 'FMCG'
        
        return f"{total} FMCG {'deals' if total > 1 else 'deal'} found, {disclosed} with disclosed values. {top_cat.capitalize()} sector showing most activity."
    
    def to_markdown(self, newsletter: Dict) -> str:
        """Convert to markdown"""
        md = [
            f"# {newsletter.get('title', 'FMCG M&A Briefing')}",
            f"*{newsletter.get('date', datetime.now().strftime('%B %d, %Y'))}*",
            "",
            "## Summary",
            newsletter.get('summary', 'No summary available'),
            "",
            "## Top Deals"
        ]
        
        deals = newsletter.get('deals', [])
        if deals:
            for i, d in enumerate(deals, 1):
                md.append(f"### {i}. {d.get('acquirer', 'Unknown')} → {d.get('target', 'Unknown')}")
                md.append(f"- Amount: {d.get('amount', 'Undisclosed')}")
                if d.get('credibility'):
                    md.append(f"- Credibility: {d.get('credibility')}/100")
                if d.get('summary'):
                    md.append(f"- Summary: {d.get('summary')}")
                md.append("")
        else:
            md.append("No deals found")
            md.append("")
        
        md.append("## Trends")
        trends = newsletter.get('trends', [])
        if trends:
            for t in trends:
                md.append(f"- {t}")
        else:
            md.append("- No trends identified")
        
        return '\n'.join(md)