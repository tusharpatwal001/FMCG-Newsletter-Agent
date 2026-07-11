# FMCG M&A Intelligence Newsletter Agent

An automated, intelligent pipeline for monitoring FMCG (Fast-Moving Consumer Goods) industry acquisitions, mergers, deals, and buyouts. The system fetches real-time news, deduplicates content, filters for relevance, scores credibility, and generates a curated newsletter with AI-powered summarization.

## 🎯 Overview

The FMCG Newsletter Agent is a sophisticated news aggregation and analysis system built with Python. It automates the end-to-end process of:
- **Collecting** FMCG M&A news from Google Search via the Serper API
- **Deduplicating** similar articles to avoid redundancy
- **Filtering** for relevance to M&A activities
- **Scoring** articles based on source credibility and content signals
- **Generating** a professional newsletter with optional AI summarization using OpenAI's LLM

Perfect for investment analysts, business intelligence teams, and industry professionals tracking consolidation trends in the FMCG sector.

## ✨ Features

- **Real-time News Collection**: Fetches articles from Google Search with flexible time range filters
- **Smart Deduplication**: Identifies and removes duplicate articles using similarity detection
- **Relevance Filtering**: Automatically filters articles relevant to M&A activities
- **Credibility Scoring**: Evaluates source credibility and content quality
- **AI Summarization**: Optional LLM-powered summaries using OpenAI's API
- **Interactive Dashboard**: Streamlit-based web interface for configuration and monitoring
- **Configurable Filters**: Adjust time ranges, credibility thresholds, and other parameters
- **Processing Metrics**: Real-time visibility into pipeline performance

## 📁 Project Structure

```
.
├── app.py                          # Main Streamlit application
├── test_pipeline.py                # Pipeline testing script
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Project configuration
├── README.md                       # This file
├── src/
│   ├── __init__.py
│   ├── news_collector.py           # Serper API integration for article fetching
│   ├── deduplicator.py             # Duplicate detection and removal
│   ├── relevance_filter.py         # M&A relevance classification
│   ├── credibility_scorer.py       # Source and content credibility scoring
│   └── newsletter_generator.py     # Newsletter generation with optional LLM
└── test_data/                      # Sample data for testing
    ├── ethanol-in-en-*.json        # Test datasets
    └── FMCG*.json                  # Sample FMCG M&A articles
```

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- API Keys:
  - **Serper API Key**: For accessing Google Search results ([Get one here](https://serper.dev))
  - **OpenAI API Key** (optional): For AI-powered summarization

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "FMCG Newsletter Agent"
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the project root:
   ```env
   NEWS_API_KEY=your_serper_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here  # Optional, for AI summarization
   ```

### Running the Application

**Start the Streamlit dashboard:**
```bash
streamlit run app.py
```

The application will open at `http://localhost:8501` in your browser.

## 🔧 Configuration

In the Streamlit sidebar, configure:

| Setting | Options | Default | Notes |
|---------|---------|---------|-------|
| **Time Range** | any_time, past_hour, past_day, past_week, past_month, past_year | past_month | Controls article recency |
| **API Key** | Your Serper API key | - | Required for fetching articles |
| **Min Credibility Score** | 30-80 | 50 | Higher values filter lower-quality sources |
| **AI Summarization** | Checkbox | Disabled | Requires OpenAI API key |

## 🔄 Pipeline Stages

1. **News Collection** → Fetches raw articles from Google Search
2. **Deduplication** → Identifies and removes duplicate articles
3. **Relevance Filtering** → Selects only M&A-related articles
4. **Credibility Scoring** → Evaluates source and content quality
5. **Newsletter Generation** → Compiles curated newsletter with summaries

## 📊 Output Metrics

After processing, the dashboard displays:
- **Raw Articles**: Total articles fetched
- **After Dedupe**: Articles remaining after deduplication
- **Relevant Deals**: M&A-related articles
- **Final Selected**: High-credibility articles meeting all filters

## 🧪 Testing

Run the test pipeline to validate all components:
```bash
python test_pipeline.py
```

## 📦 Dependencies

Key libraries:
- **streamlit**: Interactive web dashboard
- **langchain**: LLM orchestration
- **langchain-openai**: OpenAI integration
- **requests**: HTTP client for API calls
- **scikit-learn**: Machine learning for similarity detection
- **pandas**: Data manipulation
- **python-dotenv**: Environment variable management

See `requirements.txt` for complete list with versions.

## 🎓 Use Cases

- **Investment Firms**: Track M&A opportunities in FMCG
- **Market Research**: Monitor consolidation trends
- **Competitive Intelligence**: Stay updated on competitor acquisitions
- **Business Development**: Identify potential partnership targets

## 💡 Tips for Best Results

- Start with `past_month` to get recent deals
- Set credibility threshold to 50-60 for balanced results
- Use AI summarization for quick executive reviews
- Run daily to stay updated on M&A activities
- Monitor the metrics dashboard to understand data patterns
