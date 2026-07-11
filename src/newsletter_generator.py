import os
import re
from datetime import datetime
from typing import List, Dict
from pydantic import SecretStr
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

api_key = os.getenv("OPEN_API_KEY")
# print(api_key)
# import sys; sys.exit(0)
if api_key is None:
    raise ValueError("OPEN_API_KEY is not set")


class NewsletterGenerator:
    """Newsletter generator with optional LangChain"""
    
    def __init__(self, use_llm: bool = False):
        self.use_llm = use_llm
        if use_llm:
            self.llm = ChatOpenAI(model="gpt-5-nano", temperature=0.3, reasoning=None ,api_key=SecretStr(api_key)) # type: ignore
            self.prompt = ChatPromptTemplate.from_template(
                "Summarize these FMCG deals in 2 sentences: {deals}"
            )
            self.chain =  self.prompt | self.llm

    
    def generate(self, articles: List[Dict]) -> Dict:
        """Generate newsletter from articles"""
        if not articles:
            return {'title': 'FMCG Briefing', 'date': datetime.now().strftime('%B %d, %Y'), 
                    'summary': 'No deals found', 'deals': [], 'trends': []}
        
        # Extract deals
        deals = []
        for a in articles[:10]:
            text = a.get('title', '') + ' ' + a.get('snippet', '')
            if any(w in text.lower() for w in ['acquire', 'buyout', 'stake', 'merger']):
                deal = self._parse_deal(text)
                if deal:
                    deals.append(deal)
        
        # Generate summary
        summary = self._summary(deals) if deals else "No FMCG deals found"
        
        # Extract trends
        trends = [a['title'] for a in articles[:3] if any(w in a.get('title', '').lower() 
                  for w in ['trend', 'growth', 'shift'])]
        
        return {
            'title': 'FMCG M&A Briefing',
            'date': datetime.now().strftime('%B %d, %Y'),
            'summary': summary,
            'deals': deals[:5],
            'trends': trends[:3] or ['Increased M&A activity in FMCG sector']
        }
    
    def _parse_deal(self, text: str):
        """Extract deal info using regex"""
        # Acquirer
        acquirer = re.search(r'([A-Z][a-zA-Z\s]+?)\s+(?:acquires|buys|purchases)', text)
        acquirer = acquirer.group(1).strip() if acquirer else None
        
        # Target
        target = re.search(r'(?:acquires|buys|purchases)\s+([A-Z][a-zA-Z\s]+?)', text)
        target = target.group(1).strip() if target else None
        
        # Amount
        amount = re.search(r'(?:Rs|USD|\$)\s*[\d,]+(?:\s+crore|\s+million|\s+billion)?', text)
        
        if not acquirer or not target:
            return None
        
        return {
            'acquirer': acquirer,
            'target': target,
            'amount': amount.group(0) if amount else 'Undisclosed'
        }
    
    def _summary(self, deals: List[Dict]):
        """Generate summary with optional LLM"""
        if self.use_llm and deals:
            try:
                deals_text = "\n".join([f"{d['acquirer']} → {d['target']} ({d['amount']})" 
                                       for d in deals[:3]])
                result = self.chain.invoke({"deals":deals_text})
                return result.content
            except:  # noqa: E722
                pass
        
        # Rule-based summary
        total = len(deals)
        disclosed = len([d for d in deals if d['amount'] != 'Undisclosed'])
        return f"{total} FMCG deals found, {disclosed} with disclosed values"
    
    def to_markdown(self, newsletter: Dict) -> str:
        """Convert to markdown"""
        md = [f"# {newsletter['title']}", f"*{newsletter['date']}*", "",
              f"## Summary\n{newsletter['summary']}", "",
              "## Top Deals"]
        for i, d in enumerate(newsletter['deals'], 1):
            md.append(f"### {i}. {d['acquirer']} → {d['target']}")
            md.append(f"- Amount: {d['amount']}\n")
        md.append("## Trends")
        for t in newsletter['trends']:
            md.append(f"- {t}")
        return '\n'.join(md)
    
if __name__ == "__main__":
    demo1 = NewsletterGenerator(use_llm=True)
    result = demo1.chain.invoke({"deals":"hello"})
    # print(result)
    # print(result.content)