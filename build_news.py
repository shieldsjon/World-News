import feedparser
import json
import re
import socket
import concurrent.futures

# Prevent any individual RSS connection from hanging indefinitely
socket.setdefaulttimeout(5)


# ============================================================
# NEWS SOURCES
# ============================================================

FEEDS = [
    # ========================================================
    # MAJOR U.S. NATIONAL & WIRE DESKS
    # ========================================================

    {
        "name": "AP News Top Stories",
        "url": "https://rsshub.app/apnews/topics/ap-top-news",
        "category": "U.S.",
        "country": "United States",
        "leaning": "CENTER"
    },
    {
        "name": "NPR US News",
        "url": "https://feeds.npr.org/1001/rss.xml",
        "category": "U.S.",
        "country": "United States",
        "leaning": "CENTER"
    },
    {
        "name": "ABC News US",
        "url": "https://abcnews.go.com/abcnews/topstories",
        "category": "U.S.",
        "country": "United States",
        "leaning": "CENTER"
    },
    {
        "name": "CBS News Main",
        "url": "https://www.cbsnews.com/latest/rss/main",
        "category": "U.S.",
        "country": "United States",
        "leaning": "CENTER"
    },
    {
        "name": "NBC News Top Stories",
        "url": "https://feeds.nbcnews.com/nbcnews/public/news",
        "category": "U.S.",
        "country": "United States",
        "leaning": "CENTER"
    },
    {
        "name": "PBS NewsHour",
        "url": "https://www.pbs.org/newshour/feeds/news_feed",
        "category": "U.S.",
        "country": "United States",
        "leaning": "CENTER"
    },
    {
        "name": "USA Today",
        "url": "https://rssfeeds.usatoday.com/usatoday-newstopstories",
        "category": "U.S.",
        "country": "United States",
        "leaning": "CENTER"
    },
    {
        "name": "Politico US",
        "url": "https://www.politico.com/rss/politicopics.xml",
        "category": "Governance",
        "country": "United States",
        "leaning": "LEFT"
    },
    {
        "name": "The Hill",
        "url": "https://thehill.com/feed/",
        "category": "Governance",
        "country": "United States",
        "leaning": "CENTER"
    },

    # ========================================================
    # MAJOR U.S. METROPOLITAN & REGIONAL NEWSPAPERS
    # ========================================================

    {
        "name": "Washington Post World",
        "url": "https://feeds.washingtonpost.com/rss/world",
        "category": "U.S.",
        "country": "United States",
        "leaning": "LEFT"
    },
    {
        "name": "Los Angeles Times",
        "url": "https://www.latimes.com/world-nation/rss2.0.xml",
        "category": "U.S.",
        "country": "United States",
        "leaning": "LEFT"
    },
    {
        "name": "Chicago Tribune",
        "url": "https://www.chicagotribune.com/feed/",
        "category": "U.S.",
        "country": "United States",
        "leaning": "CENTER"
    },
    {
        "name": "Boston Globe",
        "url": "https://www.bostonglobe.com/arc/outboundfeeds/rss/?category=news",
        "category": "U.S.",
        "country": "United States",
        "leaning": "LEFT"
    },
    {
        "name": "San Francisco Chronicle",
        "url": "https://www.sfchronicle.com/bayarea/feed/Bay-Area-News-299.php",
        "category": "U.S.",
        "country": "United States",
        "leaning": "LEFT"
    },
    {
        "name": "Miami Herald",
        "url": "https://www.miamiherald.com/news/local/?format=rss",
        "category": "U.S.",
        "country": "United States",
        "leaning": "LEFT"
    },
    {
        "name": "Dallas Morning News",
        "url": "https://www.dallasnews.com/arc/outboundfeeds/rss/",
        "category": "U.S.",
        "country": "United States",
        "leaning": "CENTER"
    },
    {
        "name": "Seattle Times",
        "url": "https://www.seattletimes.com/feed/",
        "category": "U.S.",
        "country": "United States",
        "leaning": "LEFT"
    },
    {
        "name": "Denver Post",
        "url": "https://www.denverpost.com/feed/",
        "category": "U.S.",
        "country": "United States",
        "leaning": "LEFT"
    },

    # ========================================================
    # CANADA
    # ========================================================

    {
        "name": "CBC News Canada",
        "url": "https://www.cbc.ca/cbbc/lineup/topstories.xml",
        "category": "World",
        "country": "Canada",
        "leaning": "CENTER"
    },
    {
        "name": "CTV News Canada",
        "url": "https://www.ctvnews.ca/rss/ctvnews-ca-top-stories-public-rss-1.822009",
        "category": "World",
        "country": "Canada",
        "leaning": "CENTER"
    },
    {
        "name": "Globe and Mail",
        "url": "https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/world/",
        "category": "World",
        "country": "Canada",
        "leaning": "CENTER"
    },
    {
        "name": "Global News Canada",
        "url": "https://globalnews.ca/feed/",
        "category": "World",
        "country": "Canada",
        "leaning": "CENTER"
    },
    {
        "name": "Toronto Star",
        "url": "https://www.thestar.com/search/?f=rss&t=article&c=news*",
        "category": "U.S.",
        "country": "Canada",
        "leaning": "LEFT"
    },
    {
        "name": "National Post",
        "url": "https://nationalpost.com/feed/",
        "category": "World",
        "country": "Canada",
        "leaning": "RIGHT"
    },
    {
        "name": "CBC Politics",
        "url": "https://www.cbc.ca/webfeed/rss/rss-politics",
        "category": "Governance",
        "country": "Canada",
        "leaning": "CENTER"
    },

    # ========================================================
    # BUSINESS & ECONOMY
    # ========================================================

    {
        "name": "CNBC Business",
        "url": "https://search.cnbc.com/rs/search/combinedrender?source=0&id=100003114&trendline=38&categories=100003114&partnerId=2000&keywords=1",
        "category": "Economy",
        "country": "United States",
        "leaning": "CENTER"
    },
    {
        "name": "NPR Business",
        "url": "https://feeds.npr.org/1017/rss.xml",
        "category": "Economy",
        "country": "United States",
        "leaning": "CENTER"
    },
    {
        "name": "MarketWatch",
        "url": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
        "category": "Economy",
        "country": "United States",
        "leaning": "CENTER"
    },
    {
        "name": "Bloomberg Markets",
        "url": "https://news.google.com/rss/search?q=when:24h+site:bloomberg.com&hl=en-US&gl=US&ceid=US:en",
        "category": "Economy",
        "country": "United States",
        "leaning": "CENTER"
    },
    {
        "name": "Wall Street Journal",
        "url": "https://news.google.com/rss/search?q=when:24h+site:wsj.com&hl=en-US&gl=US&ceid=US:en",
        "category": "Economy",
        "country": "United States",
        "leaning": "RIGHT"
    },

    # ========================================================
    # SPORTS
    # ========================================================

    {
        "name": "ESPN Top Stories",
        "url": "https://www.espn.com/espn/rss/news",
        "category": "Sports",
        "country": "United States",
        "leaning": "CENTER"
    },
    {
        "name": "CBC Sports",
        "url": "https://www.cbc.ca/webfeed/rss/rss-sports",
        "category": "Sports",
        "country": "Canada",
        "leaning": "CENTER"
    },
    {
        "name": "TSN Sports Canada",
        "url": "https://www.tsn.ca/rss",
        "category": "Sports",
        "country": "Canada",
        "leaning": "CENTER"
    },
    {
        "name": "Sports Illustrated",
        "url": "https://www.si.com/.rss/full/",
        "category": "Sports",
        "country": "United States",
        "leaning": "CENTER"
    },
    {
        "name": "BBC Sports Desk",
        "url": "https://feeds.bbci.co.uk/sport/rss.xml",
        "category": "Sports",
        "country": "United Kingdom",
        "leaning": "CENTER"
    },

    # ========================================================
    # TECH / SCIENCE / ENVIRONMENT
    # ========================================================

    {
        "name": "NPR Tech",
        "url": "https://feeds.npr.org/1019/rss.xml",
        "category": "Tech",
        "country": "United States",
        "leaning": "CENTER"
    },
    {
        "name": "NPR Science",
        "url": "https://feeds.npr.org/1007/rss.xml",
        "category": "Tech",
        "country": "United States",
        "leaning": "CENTER"
    },
    {
        "name": "Wired Tech",
        "url": "https://www.wired.com/feed/rss",
        "category": "Tech",
        "country": "United States",
        "leaning": "LEFT"
    },
    {
        "name": "NASA Science",
        "url": "https://www.nasa.gov/rss/dyn/breaking_news.rss",
        "category": "Tech",
        "country": "United States",
        "leaning": "CENTER"
    },
    {
        "name": "TechCrunch",
        "url": "https://techcrunch.com/feed/",
        "category": "Tech",
        "country": "United States",
        "leaning": "CENTER"
    },
    {
        "name": "Ars Technica",
        "url": "https://feeds.arstechnica.com/arstechnica/index",
        "category": "Tech",
        "country": "United States",
        "leaning": "CENTER"
    },
    {
        "name": "EcoWatch Climate",
        "url": "https://www.ecowatch.com/feeds/feed.rss",
        "category": "Climate",
        "country": "United States",
        "leaning": "LEFT"
    },
    {
        "name": "Smithsonian Magazine",
        "url": "https://www.smithsonianmag.com/rss/latest_articles/",
        "category": "Arts",
        "country": "United States",
        "leaning": "CENTER"
    },
    {
        "name": "NPR Arts & Culture",
        "url": "https://feeds.npr.org/1008/rss.xml",
        "category": "Arts",
        "country": "United States",
        "leaning": "CENTER"
    },

    # ========================================================
    # INTERNATIONAL
    # ========================================================

    {
        "name": "BBC News World",
        "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "category": "World",
        "country": "United Kingdom",
        "leaning": "CENTER"
    },
    {
        "name": "Al Jazeera English",
        "url": "https://www.aljazeera.com/xml/rss/all.xml",
        "category": "World",
        "country": "International",
        "leaning": "CENTER"
    },
    {
        "name": "NPR World News",
        "url": "https://feeds.npr.org/1004/rss.xml",
        "category": "World",
        "country": "United States",
        "leaning": "CENTER"
    },
    {
        "name": "Deutsche Welle",
        "url": "https://rss.dw.com/rdf/rss-en-world",
        "category": "Governance",
        "country": "Germany",
        "leaning": "CENTER"
    },
    {
        "name": "France 24",
        "url": "https://www.france24.com/en/rss",
        "category": "World",
        "country": "France",
        "leaning": "CENTER"
    },
    {
        "name": "The Guardian",
        "url": "https://www.theguardian.com/world/rss",
        "category": "World",
        "country": "United Kingdom",
        "leaning": "LEFT"
    },
    {
        "name": "UN News",
        "url": "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
        "category": "Climate",
        "country": "International",
        "leaning": "CENTER"
    },
]


# ============================================================
# FEEL-GOOD FILTER
# ============================================================

POSITIVE_WORDS = [
    "breakthrough",
    "discovery",
    "conservation",
    "restored",
    "clean energy",
    "pact signed",
    "milestone reached",
    "wildlife recovery",
    "cured",
    "graduated",
    "innovation",
    "humanitarian aid",
    "community success",
    "renewable record",
    "thrive"
]

NEGATIVE_BLOCKLIST = [
    "kill",
    "strike",
    "war",
    "stalled",
    "dead",
    "death",
    "conflict",
    "crisis",
    "attack",
    "shooting",
    "injured",
    "crash",
    "disaster",
    "threat",
    "warning",
    "hostage",
    "bomb",
    "collapse",
    "charges",
    "arrest",
    "scandal",
    "probe"
]


def is_truly_feel_good(text):
    lower = text.lower()

    if any(negative in lower for negative in NEGATIVE_BLOCKLIST):
        return False

    return any(positive in lower for positive in POSITIVE_WORDS)


# ============================================================
# FETCH EACH SOURCE
# ============================================================

def parse_feed(feed_info):
    feed_stories = []

    try:
        parsed = feedparser.parse(feed_info["url"])
        entries = parsed.entries[:10]

        for entry in entries:

            title = entry.get("title", "").strip()

            if not title:
                continue

            raw_summary = entry.get(
                "summary",
                entry.get("description", "")
            )

            summary = re.sub(
                r"<[^<]+?>",
                "",
                raw_summary
            ).strip()

            if len(summary) > 250:
                summary = summary[:250] + "..."

            if not summary:
                summary = "Direct headline coverage from bureau wire."

            combined_text = title + " " + summary

            feel_good_status = is_truly_feel_good(
                combined_text
            )

            feed_stories.append({

                "title": title,

                "category": feed_info["category"],

                "country": feed_info["country"],

                "leaning": feed_info.get(
                    "leaning",
                    "CENTER"
                ),

                "feelGood": feel_good_status,

                "keyFacts": [
                    summary,
                    f"Reporting Desk: {feed_info['name']}",
                    f"Source Stamp: {entry.get('published', 'Recent Wire')}"
                ],

                "sources": [
                    {
                        "name": feed_info["name"],
                        "url": entry.get("link", "#"),
                        "bias": feed_info.get(
                            "leaning",
                            "CENTER"
                        )
                    }
                ]
            })

    except Exception as e:
        print(
            f"Skipped {feed_info['name']}: {e}"
        )

    return feed_stories


# ============================================================
# BUILD NEWS.JSON
# ============================================================

def main():

    print(
        f"Fetching from {len(FEEDS)} "
        "North American & International feeds..."
    )

    all_raw_stories = []

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=25
    ) as executor:

        results = executor.map(
            parse_feed,
            FEEDS
        )

        for result in results:
            all_raw_stories.extend(result)

    unique_stories = []

    seen_titles = set()

    for story in all_raw_stories:

        title_key = story["title"].lower().strip()

        if title_key not in seen_titles:

            seen_titles.add(title_key)

            story["id"] = (
                f"story-{len(unique_stories) + 1}"
            )

            unique_stories.append(story)

    with open(
        "news.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            unique_stories,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"Successfully compiled "
        f"{len(unique_stories)} stories into news.json"
    )


if __name__ == "__main__":
    main()
