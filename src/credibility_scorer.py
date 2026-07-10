import re
from datetime import datetime


class CredibilityScorer:
    def __init__(self):
        # Domain authority score (1-100)
        self.domain_scores = {
            "economictimes.indiatimes.com": 85,
            "financialexpress.com": 80,
            "reuters.com": 90,
            "bloomberg.com": 90,
            "forbes": 75,
            "business-standard.com": 75,
            "cnbc.com": 85,
            "ft.com": 90,
            "bbc.com": 80,
            "intellizence.com": 65,
        }

    def score_article(self, article):
        """Calculate credibility score with transparency"""
        score = 0
        reasons = []

        # 1. Domain authority (max 40 points)
        domain = article.get("link", {})
        found_domain = [i for i in self.domain_scores if i in domain]

        domain_score = self.domain_scores.get(
            found_domain[-1] if len(found_domain) > 0 else domain, 30
        )
        score += domain_score * 0.8
        reasons.append(f"Domain authority: {domain_score}/100")

        # 2. Quotations (15 points)
        if re.search(r'"[^"]+"', article.get("snippet", "")):
            score += 15
            reasons.append("Direct quotations: +15")

        # 3. Deal specificity (25 points)
        content = article.get("snippet", "")
        if re.search(
            r"Rs\s+[\d,]+ crore|Rs\s+[\d,]+ million|\$\s+[\d,]+ million|\$\s+[\d,]+ billion",
            content,
        ):
            score += 25
            reasons.append("Specific deal amount: +25")
        elif re.search(r"acquire|buyout|stake|acquisition|merger", content):
            score += 10
            reasons.append("Deal terms mentioned: +10")

        # 4. Recency (10 points)
        # Articles from last 30 days get bonus
        days_old = (
            datetime.now() - datetime.strptime(article["date"], "%b %d, %Y")
        ).days
        if days_old <= 30:
            score += 10
            reasons.append("Recent (<= days): +10")

        return {
            "score": min(score, 100),
            "breakdown": reasons,
            "threshold": score >= 50,
        }


if __name__ == "__main__":
    dem1 = CredibilityScorer()
    with open(
        "test_data/FMCG acquisition merger deal buyout-us-en-true-1-10-search-qdr_y.json",
        encoding="utf-8",
    ) as f:
        import json

        data = json.load(f)
        # print(data[-1]['organic'])

    for arti in data[-1]["organic"]:
        print(dem1.score_article(arti))
        # import sys; sys.exit(0)
