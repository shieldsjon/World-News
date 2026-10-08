import feedparser
import json
import re

# Add as many feeds as you want here (50, 100, 200+)
FEEDS = [
    # World / Global Desks
    {"name": "BBC News World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml", "category": "World", "country": "United Kingdom"},
    {"name": "Al Jazeera English", "url": "https://www.aljazeera.com/xml/rss/all.xml", "category": "World", "country": "International"},
    {"name": "NPR World News", "url": "https://feeds.npr.org/1004/rss.xml", "category": "World", "country": "United States"},
    {"name": "Deutsche Welle", "url": "https://rss.dw.com/rdf/rss-en-world", "category": "Governance", "country": "Germany"},
    {"name": "France 24", "url": "https://www.france24.com/en/rss", "category": "World", "country": "France"},
    {"name": "CBC News", "url": "https://www.cbc.ca/cbbc/lineup/topstories.xml", "category": "World", "country": "Canada"},
    {"name": "The Guardian", "url": "https://www.theguardian.com/world/rss", "category": "World", "country": "United Kingdom"},
    {"name": "UN News", "url": "https://news.un.org/feed/subscribe/en/news/all/rss.xml", "category": "Climate", "country": "International"},

    # Regional & International Desks
    {"name": "Japan Today", "url": "https://japantoday.com/feed", "category": "World", "country": "Japan"},
    {"name": "The Straits Times", "url": "https://www.straitstimes.com/news/world/rss.xml", "category": "World", "country": "Singapore"},
    {"name": "The Hindu", "url": "https://www.thehindu.com/news/international/feeder/default.rss", "category": "World", "country": "India"},
    {"name": "South China Morning Post", "url": "https://www.scmp.com/rss/91/feed", "category": "World", "country": "China"},
    {"name": "EuroNews", "url": "https://www.euronews.com/rss?format=mrss&level=theme&name=news", "category": "World", "country": "International"},
    {"name": "Politico Europe", "url": "https://www.politico.eu/feed/", "category": "Governance", "country": "Germany"},
    {"name": "SBS Australia", "url": "https://www.sbs.com.au/news/feed", "category": "World", "country": "Australia"},
    {"name": "Sydney Morning Herald", "url": "https://www.smh.com.au/rss/feed.xml", "category": "World", "country": "Australia"},
    {"name": "RFI France", "url": "https://www.rfi.fr/en/general/rss", "category": "World", "country": "France"},
    {"name": "Buenos Aires Times", "url": "https://www.batimes.com.ar/feed", "category": "World", "country": "Argentina"},

    # Topical & Specialist Desks
    {"name": "NPR Tech", "url": "https://feeds.npr.org/1019/rss.xml", "category": "Tech", "country": "United States"},
    {"name": "Wired Tech", "url": "https://www.wired.com/feed/rss", "category": "Tech", "country": "United States"},
    {"name": "NASA Science", "url": "https://www.nasa.gov/rss/dyn/breaking_news.rss", "category": "Tech", "country": "United States"},
    {"name": "CNBC Markets", "url": "https://search.cnbc.com/rs/search/combinedrender?source=0&id=100003114&trendline=38&categories=100003114&partnerId=2000&keywords=1", "category": "Economy", "country": "United States"},
    {"name": "NPR Business", "url": "https://feeds.npr.org/1017/rss.xml", "category": "Economy", "country": "United States"},
    {"name": "EcoWatch Climate", "url": "https://www.ecowatch.com/feeds/feed.rss", "category": "Climate", "country": "United States"},
    {"name": "BBC Sports", "url": "https://feeds.bbci.co.uk/sport/rss.xml", "category": "Sports", "country": "United Kingdom"},
    {"name": "NPR Arts & Culture", "url": "https://feeds.npr.org/1008/rss.xml", "category": "Arts", "country": "United States"}
]

POSITIVE_WORDS = [
    'win', 'breakthrough', 'peace', 'save', 'hope', 'discovery', 'grant', 
    'aid', 'conservation', 'restored', 'clean', 'agree', 'award', 'pact', 
    'solution', 'cured', 'progress', 'milestone', 'agreement'
]

stories = []
seen_titles = set()

print(f"Starting news pull from {len(FEEDS)} feeds...")

for feed_info in FEEDS:
    try:
        parsed = feedparser.parse(feed_info["url"])
        entries = parsed.entries[:10]  # Take top 10 from each feed
        
        for entry in entries:
            title = entry.get("title", "").strip()
            if not title or title.lower() in seen_titles:
                continue
            
            seen_titles.add(title.lower())
            
            # Clean HTML out of summary descriptions
            raw_summary = entry.get("summary", entry.get("description", ""))
            summary = re.sub('<[^<]+?>', '', raw_summary).strip()
            if len(summary) > 250:
                summary = summary[:250] + "..."
            elif not summary:
                summary = "Direct headline coverage from bureau wire."

            is_feel_good = any(word in (title + " " + summary).lower() for word in POSITIVE_WORDS)

            stories.append({
                "id": f"{feed_info['name'].replace(' ', '')}-{len(stories)}",
                "title": title,
                "category": feed_info["category"],
                "country": feed_info["country"],
                "feelGood": is_feel_good,
                "keyFacts": [
                    summary,
                    f"Reporting Desk: {feed_info['name']}",
                    f"Source Stamp: {entry.get('published', 'Recent Wire')}"
                ],
                "sources": [{
                    "name": feed_info["name"],
                    "url": entry.get("link", "#"),
                    "bias": "Independent Reporting"
                }]
            })
    except Exception as e:
        print(f"Skipping {feed_info['name']} due to error: {e}")

# Save output file
with open("news.json", "w", encoding="utf-8") as f:
    json.dump(stories, f, indent=2, ensure_ascii=False)

print(f"Done! Successfully wrote {len(stories)} unique stories to news.json")
