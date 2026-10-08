import feedparser
import json
import re
import socket
import concurrent.futures

# Set global timeout to 5 seconds per HTTP request to prevent hangs
socket.setdefaulttimeout(5)

# Comprehensive catalog heavily prioritizing North American news desks alongside global bureaus
FEEDS = [
    # --- MAJOR U.S. NATIONAL & WIRE DESKS ---
    {"name": "AP News Top Stories", "url": "https://rsshub.app/apnews/topics/ap-top-news", "category": "U.S.", "country": "United States"},
    {"name": "NPR US News", "url": "https://feeds.npr.org/1001/rss.xml", "category": "U.S.", "country": "United States"},
    {"name": "ABC News US", "url": "https://abcnews.go.com/abcnews/topstories", "category": "U.S.", "country": "United States"},
    {"name": "CBS News Main", "url": "https://www.cbsnews.com/latest/rss/main", "category": "U.S.", "country": "United States"},
    {"name": "NBC News Top Stories", "url": "https://feeds.nbcnews.com/nbcnews/public/news", "category": "U.S.", "country": "United States"},
    {"name": "PBS NewsHour", "url": "https://www.pbs.org/newshour/feeds/news_feed", "category": "U.S.", "country": "United States"},
    {"name": "USA Today", "url": "https://rssfeeds.usatoday.com/usatoday-newstopstories", "category": "U.S.", "country": "United States"},
    {"name": "Politico US", "url": "https://www.politico.com/rss/politicopics.xml", "category": "Governance", "country": "United States"},
    {"name": "The Hill", "url": "https://thehill.com/feed/", "category": "Governance", "country": "United States"},

    # --- MAJOR METROPOLITAN & REGIONAL U.S. NEWSPAPERS ---
    {"name": "Washington Post World", "url": "https://feeds.washingtonpost.com/rss/world", "category": "U.S.", "country": "United States"},
    {"name": "Los Angeles Times", "url": "https://www.latimes.com/world-nation/rss2.0.xml", "category": "U.S.", "country": "United States"},
    {"name": "Chicago Tribune", "url": "https://www.chicagotribune.com/feed/", "category": "U.S.", "country": "United States"},
    {"name": "Boston Globe", "url": "https://www.bostonglobe.com/arc/outboundfeeds/rss/?category=news", "category": "U.S.", "country": "United States"},
    {"name": "San Francisco Chronicle", "url": "https://www.sfchronicle.com/bayarea/feed/Bay-Area-News-299.php", "category": "U.S.", "country": "United States"},
    {"name": "Miami Herald", "url": "https://www.miamiherald.com/news/local/?format=rss", "category": "U.S.", "country": "United States"},
    {"name": "Dallas Morning News", "url": "https://www.dallasnews.com/arc/outboundfeeds/rss/", "category": "U.S.", "country": "United States"},
    {"name": "Seattle Times", "url": "https://www.seattletimes.com/feed/", "category": "U.S.", "country": "United States"},
    {"name": "Denver Post", "url": "https://www.denverpost.com/feed/", "category": "U.S.", "country": "United States"},

    # --- CANADIAN NATIONAL & REGIONAL NEWS ---
    {"name": "CBC News Canada", "url": "https://www.cbc.ca/cbbc/lineup/topstories.xml", "category": "World", "country": "Canada"},
    {"name": "CTV News Canada", "url": "https://www.ctvnews.ca/rss/ctvnews-ca-top-stories-public-rss-1.822009", "category": "World", "country": "Canada"},
    {"name": "Globe and Mail", "url": "https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/world/", "category": "World", "country": "Canada"},
    {"name": "Global News Canada", "url": "https://globalnews.ca/feed/", "category": "World", "country": "Canada"},
    {"name": "Toronto Star", "url": "https://www.thestar.com/search/?f=rss&t=article&c=news*", "category": "U.S.", "country": "Canada"},
    {"name": "National Post", "url": "https://nationalpost.com/feed/", "category": "World", "country": "Canada"},
    {"name": "CBC Politics", "url": "https://www.cbc.ca/webfeed/rss/rss-politics", "category": "Governance", "country": "Canada"},

    # --- NORTH AMERICAN BUSINESS & ECONOMY ---
    {"name": "CNBC Business", "url": "https://search.cnbc.com/rs/search/combinedrender?source=0&id=100003114&trendline=38&categories=100003114&partnerId=2000&keywords=1", "category": "Economy", "country": "United States"},
    {"name": "NPR Business", "url": "https://feeds.npr.org/1017/rss.xml", "category": "Economy", "country": "United States"},
    {"name": "MarketWatch", "url": "https://feeds.content.dowjones.io/public/rss/mw_topstories", "category": "Economy", "country": "United States"},
    {"name": "Bloomberg Markets (RSS)", "url": "https://news.google.com/rss/search?q=when:24h+site:bloomberg.com&hl=en-US&gl=US&ceid=US:en", "category": "Economy", "country": "United States"},
    {"name": "Wall Street Journal (RSS)", "url": "https://news.google.com/rss/search?q=when:24h+site:wsj.com&hl=en-US&gl=US&ceid=US:en", "category": "Economy", "country": "United States"},

    # --- NORTH AMERICAN SPORTS ---
    {"name": "ESPN Top Stories", "url": "https://www.espn.com/espn/rss/news", "category": "Sports", "country": "United States"},
    {"name": "CBC Sports", "url": "https://www.cbc.ca/webfeed/rss/rss-sports", "category": "Sports", "country": "Canada"},
    {"name": "TSN Sports Canada", "url": "https://www.tsn.ca/rss", "category": "Sports", "country": "Canada"},
    {"name": "Sports Illustrated", "url": "https://www.si.com/.rss/full/", "category": "Sports", "country": "United States"},

    # --- NORTH AMERICAN TECH, SCIENCE & ENVIRONMENT ---
    {"name": "NPR Tech", "url": "https://feeds.npr.org/1019/rss.xml", "category": "Tech", "country": "United States"},
    {"name": "NPR Science", "url": "https://feeds.npr.org/1007/rss.xml", "category": "Tech", "country": "United States"},
    {"name": "Wired Tech", "url": "https://www.wired.com/feed/rss", "category": "Tech", "country": "United States"},
    {"name": "NASA Science", "url": "https://www.nasa.gov/rss/dyn/breaking_news.rss", "category": "Tech", "country": "United States"},
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "category": "Tech", "country": "United States"},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index", "category": "Tech", "country": "United States"},
    {"name": "EcoWatch Climate", "url": "https://www.ecowatch.com/feeds/feed.rss", "category": "Climate", "country": "United States"},
    {"name": "Smithsonian Magazine", "url": "https://www.smithsonianmag.com/rss/latest_articles/", "category": "Arts", "country": "United States"},
    {"name": "NPR Arts & Culture", "url": "https://feeds.npr.org/1008/rss.xml", "category": "Arts", "country": "United States"},

    # --- INTERNATIONAL BALANCING DESKS ---
    {"name": "BBC News World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml", "category": "World", "country": "United Kingdom"},
    {"name": "Al Jazeera English", "url": "https://www.aljazeera.com/xml/rss/all.xml", "category": "World", "country": "International"},
    {"name": "Deutsche Welle", "url": "https://rss.dw.com/rdf/rss-en-world", "category": "Governance", "country": "Germany"},
    {"name": "France 24", "url": "https://www.france24.com/en/rss", "category": "World", "country": "France"},
    {"name": "The Guardian", "url": "https://www.theguardian.com/world/rss", "category": "World", "country": "United Kingdom"},
    {"name": "UN News", "url": "https://news.un.org/feed/subscribe/en/news/all/rss.xml", "category": "Climate", "country": "International"}
]

POSITIVE_WORDS = [
    'breakthrough', 'discovery', 'conservation', 'restored', 'clean energy', 
    'pact signed', 'milestone reached', 'wildlife recovery', 'cured', 'graduated', 
    'innovation', 'humanitarian aid', 'community success', 'renewable record', 'thrive'
]

NEGATIVE_BLOCKLIST = [
    'kill', 'strike', 'war', 'stalled', 'dead', 'death', 'conflict', 'crisis', 
    'attack', 'shooting', 'injured', 'crash', 'disaster', 'threat', 'warning', 
    'hostage', 'bomb', 'collapse', 'charges', 'arrest', 'scandal', 'probe'
]

def is_truly_feel_good(text):
    lower = text.lower()
    if any(neg in lower for neg in NEGATIVE_BLOCKLIST):
        return False
    return any(pos in lower for pos in POSITIVE_WORDS)

def parse_feed(feed_info):
    feed_stories = []
    try:
        parsed = feedparser.parse(feed_info["url"])
        entries = parsed.entries[:10]
        
        for entry in entries:
            title = entry.get("title", "").strip()
            if not title:
                continue
            
            raw_summary = entry.get("summary", entry.get("description", ""))
            summary = re.sub('<[^<]+?>', '', raw_summary).strip()
            if len(summary) > 250:
                summary = summary[:250] + "..."
            elif not summary:
                summary = "Direct headline coverage from bureau wire."

            combined_text = title + " " + summary
            feel_good_status = is_truly_feel_good(combined_text)

            feed_stories.append({
                "title": title,
                "category": feed_info["category"],
                "country": feed_info["country"],
                "feelGood": feel_good_status,
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
        print(f"Skipped {feed_info['name']}: {e}")
    return feed_stories

def main():
    print(f"Fetching from {len(FEEDS)} North American & International feeds...")
    all_raw_stories = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        results = executor.map(parse_feed, FEEDS)
        for res in results:
            all_raw_stories.extend(res)

    unique_stories = []
    seen_titles = set()

    for story in all_raw_stories:
        title_key = story["title"].lower().strip()
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            story["id"] = f"story-{len(unique_stories) + 1}"
            unique_stories.append(story)

    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(unique_stories, f, indent=2, ensure_ascii=False)

    print(f"Successfully compiled {len(unique_stories)} North American & global stories into news.json")

if __name__ == "__main__":
    main()
