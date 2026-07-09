import os
import requests
from dotenv import load_dotenv

load_dotenv()


class FMCGNewsCollector:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/search"
        self.query = "FMCG acquisition merger deal buyout"

    def fetch_articles(self, time_line: str = "past_year"):
        """
        Fetch FMCG acquisition, merger, deal, and buyout-related news articles
        from Google Search using the Serper API.

        Args:
            time_line (str, optional):
                Specifies the time range for filtering search results.
                Supported values are:

                - "any_time"   : Search without a time restriction.
                - "past_hour"  : Articles published within the last hour.
                - "past_day"   : Articles published within the last 24 hours.
                - "past_week"  : Articles published within the last 7 days.
                - "past_month" : Articles published within the last 30 days.
                - "past_year"  : Articles published within the last year.
                  (Default)

        Returns:
            dict:
                A JSON response from the Serper API containing the search
                results and associated metadata.

        Raises:
            KeyError:
                If an unsupported value is provided for ``time_line``.

            requests.exceptions.RequestException:
                If the HTTP request to the Serper API fails.

        Notes:
            The search query used is:
                "FMCG acquisition merger deal buyout"

            Time filters are translated into Google's ``tbs`` parameter using:
                - qdr:a -> Any time
                - qdr:h -> Past hour
                - qdr:d -> Past day
                - qdr:w -> Past week
                - qdr:m -> Past month
                - qdr:y -> Past year
        """

        time_duration = {
            "any_time": "qdr:a",
            "past_hour": "qdr:h",
            "past_day": "qdr:d",
            "past_week": "qdr:w",
            "past_month": "qdr:m",
            "past_year": "qdr:y",
        }

        url_format = f"{self.base_url}?q={self.query.replace(" ", "+")}&tbs={time_duration[time_line]}&apiKey={self.api_key}"

        # non-dynamic url for time line
        # url_format = f"{self.base_url}?q={self.query.replace(" ", "+")}&tbs=qdr%3Ay&apiKey={self.api_key}"
        # return url_format

        response = requests.get(url=url_format)

        return response.json()


if __name__ == "__main__":
    news1 = FMCGNewsCollector(os.getenv("NEWS_API_KEY"))

    print(news1.fetch_articles())
