import re


class RelevenceFilter:
    def __init__(self):
        # FMCG keywords - expanded
        self.fmcg_keywords = [
            "FMCG",
            "CPG",
            "consumer",
            "packaged",
            "food",
            "beverage",
            "personal care",
            "home care",
            "beauty",
            "cosmetic",
            "snack",
            "biscuit",
            "dairy",
            "nutrition",
            "supplement",
        ]

        # deals keywords
        self.deal_keywords = [
            "acquisition",
            "merger",
            "buyout",
            "stake",
            "invest",
            "acquire",
            "deal",
            "buy",
            "purchase",
            "takeover",
            "investment",
            "funding",
            "raise",
            "venture",
        ]

    def is_relevant(self, article):
        """Filter for FMCG deal relevance"""
        text = f"{article['title']} {article['snippet']}".lower()

        # must contain FMCG context AND deal context
        has_fmcg = any(kw in text for kw in self.fmcg_keywords)
        has_deal = any(kw in text for kw in self.deal_keywords)

        return has_fmcg and has_deal
    



if __name__ == "__main__":
    demo1 = RelevenceFilter()
    print(demo1.deal_keywords[-1].split(", "))
