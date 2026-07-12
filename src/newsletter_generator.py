import os
import re
from datetime import datetime
from typing import List, Dict
from pydantic import SecretStr
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# api_key = os.getenv("GEMINI_API_KEY")

class NewsletterGenerator:
    """Newsletter generator with optional LangChain"""
    
    def __init__(self, use_llm: bool, api_key: str):
        self.use_llm = use_llm
        self.api_key = SecretStr(api_key)
        if use_llm:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash", 
                    temperature=0.3,
                    api_key=self.api_key
                )
                self.prompt = ChatPromptTemplate.from_template(
                    """Summarize the given link in 2-3 sentences: 
                    
                    Link:
                    {link}
                    """
                )
                self.chain = self.prompt | self.llm | StrOutputParser()

            except Exception as e:
                print(f"LLM initialization error: {e}")
                self.use_llm = False
        else:
            self.use_llm = False
    
    def generate(self, articles: List[Dict]) -> Dict:
        """Generate newsletter from articles"""
        if articles:
            # list of articles
            generated_summaries = list()
            for article in articles:
                result = self.chain.invoke({"link":article['link']})
                generated_summaries.append(result)
            return {
                'title': 'FMCG M&A Briefing',
                'date': datetime.now().strftime('%B %d, %Y'),
                'summary': "\n\n".join(generated_summaries),
                'total_generated_summaries': len(articles)
            }

        else:
            return {
                'title': 'FMCG M&A Briefing',
                'date': datetime.now().strftime('%B %d, %Y'),
                'summary': [],
                'total_generated_summaries': len(articles)
            }

    

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