from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class Deduplicator:
    def __init__(self, similarity_threshold=0.85):
        self.threshold = similarity_threshold
        self.vectorizer = TfidfVectorizer(
            max_features=1000, stop_words="english", ngram_range=(1, 2)
        )

    def find_duplicates(self, articles):
        """
        Deduplication strategy:
        1. Combine title + first 200 chars of content
        2. TF-IDF vectorization
        3. Pairwise cosine similarity > threshold
        4. Keep article with highest credibility score
        """
        texts = [f"{a['title']} {a['snippet'][:200]}" for a in articles]

        if len(texts) <= 1:
            return articles

        tfidf_matrix = self.vectorizer.fit_transform(texts)
        similarity_matrix = cosine_similarity(tfidf_matrix)

        # mark duplicates - keep highest credibility
        to_keep = []
        seen_indices = set()

        for i in range(len(articles)):
            if i in seen_indices:
                continue

            # find all articles similar to i
            duplicates = np.where(similarity_matrix[i] > self.threshold)[0]

            # choose article with best credibility
            best_idx = max(
                duplicates, key=lambda x: articles[x].get("credibility_score", 0)
            )
            to_keep.append(articles[best_idx])
            seen_indices.update(duplicates)

        return to_keep


if __name__ == "__main__":
    dummy1 = Deduplicator()
    import json

    with open(
        "ethanol-in-en-true-1-10-search-qdr_m.json",
        encoding="utf-8",
    ) as f:
        data = json.load(f)

    articles = data["organic"]

    # import sys
    # sys.exit(0)

    print(dummy1.find_duplicates(articles))
