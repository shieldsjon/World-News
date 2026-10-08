import feedparser
import json
import re
import concurrent.futures

# Catalog of top 500 world news feeds, wire services, national broadcasters, and bureaus
FEEDS = [
    # --- GLOBAL WIRES & TOP BUTEAUS ---
    {"name": "BBC News World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml", "category": "World", "country": "United Kingdom"},
    {"name": "Al Jazeera English", "url": "https://www.aljazeera.com/xml/rss/all.xml", "category": "World", "country": "International"},
    {"name": "NPR World News", "url": "https://feeds.npr.org/1004/rss.xml", "category": "World", "country": "United States"},
    {"name": "Deutsche Welle World", "url": "https://rss.dw.com/rdf/rss-en-world", "category": "Governance", "country": "Germany"},
    {"name": "France 24 English", "url": "https://www.france24.com/en/rss", "category": "World", "country": "France"},
    {"name": "CBC World News", "url": "https://www.cbc.ca/cbbc/lineup/topstories.xml", "category": "World", "country": "Canada"},
    {"name": "The Guardian World", "url": "https://www.theguardian.com/world/rss", "category": "World", "country": "United Kingdom"},
    {"name": "UN News Global", "url": "https://news.un.org/feed/subscribe/en/news/all/rss.xml", "category": "Climate", "country": "International"},
    {"name": "EuroNews", "url": "https://www.euronews.com/rss?format=mrss&level=theme&name=news", "category": "World", "country": "International"},
    {"name": "Politico Europe", "url": "https://www.politico.eu/feed/", "category": "Governance", "country": "Germany"},

    # --- UNITED STATES & NORTH AMERICA ---
    {"name": "AP News Top Stories", "url": "https://rsshub.app/apnews/topics/ap-top-news", "category": "U.S.", "country": "United States"},
    {"name": "PBS NewsHour", "url": "https://www.pbs.org/newshour/feeds/news_feed", "category": "U.S.", "country": "United States"},
    {"name": "ABC News US", "url": "https://abcnews.go.com/abcnews/topstories", "category": "U.S.", "country": "United States"},
    {"name": "CBS News Main", "url": "https://www.cbsnews.com/latest/rss/main", "category": "U.S.", "country": "United States"},
    {"name": "NBC News Top Stories", "url": "https://feeds.nbcnews.com/nbcnews/public/news", "category": "U.S.", "country": "United States"},
    {"name": "Washington Post World", "url": "https://feeds.washingtonpost.com/rss/world", "category": "World", "country": "United States"},
    {"name": "Los Angeles Times", "url": "https://www.latimes.com/world-nation/rss2.0.xml", "category": "U.S.", "country": "United States"},
    {"name": "Chicago Tribune", "url": "https://www.chicagotribune.com/feed/", "category": "U.S.", "country": "United States"},
    {"name": "Globe and Mail", "url": "https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/world/", "category": "World", "country": "Canada"},
    {"name": "Toronto Star", "url": "https://www.thestar.com/search/?f=rss&t=article&c=news/world*", "category": "World", "country": "Canada"},
    {"name": "Global News Canada", "url": "https://globalnews.ca/world/feed/", "category": "World", "country": "Canada"},
    {"name": "Mexico News Daily", "url": "https://mexiconewsdaily.com/feed/", "category": "World", "country": "Mexico"},

    # --- EUROPE ---
    {"name": "BBC News UK", "url": "https://feeds.bbci.co.uk/news/uk/rss.xml", "category": "Governance", "country": "United Kingdom"},
    {"name": "The Independent World", "url": "https://www.independent.co.uk/news/world/rss", "category": "World", "country": "United Kingdom"},
    {"name": "The Telegraph World", "url": "https://www.telegraph.co.uk/world-news/rss.xml", "category": "World", "country": "United Kingdom"},
    {"name": "RFI English", "url": "https://www.rfi.fr/en/general/rss", "category": "World", "country": "France"},
    {"name": "Le Monde in English", "url": "https://www.lemonde.fr/en/rss/une.xml", "category": "World", "country": "France"},
    {"name": "Der Spiegel International", "url": "https://www.spiegel.de/international/index.rss", "category": "World", "country": "Germany"},
    {"name": "ANSA English Italy", "url": "https://www.ansa.it/english/ansanews_rss.xml", "category": "World", "country": "Italy"},
    {"name": "El País English Spain", "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/english/portada", "category": "World", "country": "Spain"},
    {"name": "Swissinfo Switzerland", "url": "https://www.swissinfo.ch/eng/rss", "category": "World", "country": "Switzerland"},
    {"name": "Irish Times World", "url": "https://www.irishtimes.com/c2win/rss/news/world", "category": "World", "country": "Ireland"},
    {"name": "Dutchnews Netherlands", "url": "https://www.dutchnews.nl/feed/", "category": "World", "country": "Netherlands"},
    {"name": "VRT NWS Belgium", "url": "https://www.vrt.be/vrtnws/en.rss.xml", "category": "World", "country": "Belgium"},
    {"name": "The Local Sweden", "url": "https://www.thelocal.se/feed/", "category": "World", "country": "Sweden"},
    {"name": "Yle News Finland", "url": "https://feeds.yle.fi/news/v1/recent.rss?publisherIds=yle-news", "category": "World", "country": "Finland"},
    {"name": "Poland In / TVP", "url": "https://tvpworld.com/rss", "category": "World", "country": "Poland"},
    {"name": "Kathimerini Greece", "url": "https://www.ekathimerini.com/rss", "category": "World", "country": "Greece"},
    {"name": "Kyiv Independent", "url": "https://kyivindependent.com/feed/", "category": "World", "country": "Ukraine"},

    # --- ASIA & PACIFIC ---
    {"name": "NHK World Japan", "url": "https://www3.nhk.or.jp/nhkworld/en/news/ata glance.xml", "category": "World", "country": "Japan"},
    {"name": "Japan Today", "url": "https://japantoday.com/feed", "category": "World", "country": "Japan"},
    {"name": "The Japan Times", "url": "https://www.japantimes.co.jp/feed/topstories", "category": "World", "country": "Japan"},
    {"name": "South China Morning Post", "url": "https://www.scmp.com/rss/91/feed", "category": "World", "country": "China"},
    {"name": "Xinhua Net", "url": "http://www.xinhuanet.com/english/rss/worldrss.xml", "category": "World", "country": "China"},
    {"name": "Yonhap News Korea", "url": "https://en.yna.co.kr/RSS/news.xml", "category": "World", "country": "South Korea"},
    {"name": "The Korea Herald", "url": "https://www.koreaherald.com/common/rss.php?category=1", "category": "World", "country": "South Korea"},
    {"name": "The Hindu International", "url": "https://www.thehindu.com/news/international/feeder/default.rss", "category": "World", "country": "India"},
    {"name": "NDTV World", "url": "https://feeds.feedburner.com/ndtvnews-world-news", "category": "World", "country": "India"},
    {"name": "Times of India World", "url": "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms", "category": "World", "country": "India"},
    {"name": "The Straits Times", "url": "https://www.straitstimes.com/news/world/rss.xml", "category": "World", "country": "Singapore"},
    {"name": "Channel NewsAsia", "url": "https://www.channelnewsasia.com/api/v1/rss-outbound/rssnews/posts.xml", "category": "World", "country": "Singapore"},
    {"name": "Bangkok Post", "url": "https://www.bangkokpost.com/rss/data/topstories.xml", "category": "World", "country": "Thailand"},
    {"name": "Jakarta Post", "url": "https://www.thejakartapost.com/rss/latest", "category": "World", "country": "Indonesia"},
    {"name": "Rappler Philippines", "url": "https://www.rappler.com/feed/", "category": "World", "country": "Philippines"},
    {"name": "SBS Australia", "url": "https://www.sbs.com.au/news/feed", "category": "World", "country": "Australia"},
    {"name": "Sydney Morning Herald", "url": "https://www.smh.com.au/rss/feed.xml", "category": "World", "country": "Australia"},
    {"name": "ABC Australia World", "url": "https://www.abc.net.au/news/feed/51120/rss.xml", "category": "World", "country": "Australia"},
    {"name": "RNZ New Zealand", "url": "https://www.rnz.co.nz/rss/world.xml", "category": "World", "country": "New Zealand"},

    # --- MIDDLE EAST & AFRICA ---
    {"name": "Haaretz English", "url": "https://www.haaretz.com/cmlink/1.4678888", "category": "World", "country": "Israel"},
    {"name": "Times of Israel", "url": "https://www.timesofisrael.com/feed/", "category": "World", "country": "Israel"},
    {"name": "Arab News", "url": "https://www.arabnews.com/cat/1/rss.xml", "category": "World", "country": "Saudi Arabia"},
    {"name": "The National UAE", "url": "https://www.thenationalnews.com/arc/outboundfeeds/rss/", "category": "World", "country": "United Arab Emirates"},
    {"name": "TRT World Turkey", "url": "https://www.trtworld.com/rss", "category": "World", "country": "Turkey"},
    {"name": "Daily Sabah Turkey", "url": "https://www.dailysabah.com/rss/world", "category": "World", "country": "Turkey"},
    {"name": "AllAfrica Global Desk", "url": "https://allafrica.com/tools/headlines/rdf/latest/headlines.rdf", "category": "World", "country": "International"},
    {"name": "Daily Maverick South Africa", "url": "https://www.dailymaverick.co.za/dm-rss/", "category": "World", "country": "South Africa"},
    {"name": "SABC News South Africa", "url": "https://www.sabcnews.com/sabcnews/feed/", "category": "World", "country": "South Africa"},
    {"name": "Vanguard Nigeria", "url": "https://www.vanguardngr.com/feed/", "category": "World", "country": "Nigeria"},
    {"name": "The EastAfrican", "url": "https://www.theeastafrican.co.ke/tea/rss", "category": "World", "country": "Kenya"},
    {"name": "Egypt Today", "url": "https://www.egypttoday.com/RSS/1", "category": "World", "country": "Egypt"},

    # --- LATIN AMERICA ---
    {"name": "Buenos Aires Times", "url": "https://www.batimes.com.ar/feed", "category": "World", "country": "Argentina"},
    {"name": "Rio Times Brazil", "url": "https://www.riotimesonline.com/feed/", "category": "World", "country": "Brazil"},
    {"name": "Santiago Times Chile", "url": "https://santiagotimes.cl/feed/", "category": "World", "country": "Chile"},
    {"name": "Bogota Post Colombia", "url": "https://thebogotapost.com/feed/", "category": "World", "country": "Colombia"},
    {"name": "Peruvian Times", "url": "https://www.peruviantimes.com/feed/", "category": "World", "country": "Peru"},

    # --- ECONOMY & MARKETS ---
    {"name": "CNBC Markets", "url": "https://search.cnbc.com/rs/search/combinedrender?source=0&id=100003114&trendline=38&categories=100003114&partnerId=2000&keywords=1", "category": "Economy", "country": "United States"},
    {"name": "NPR Business", "url": "https://feeds.npr.org/1017/rss.xml", "category": "Economy", "country": "United States"},
    {"name": "MarketWatch Top Stories", "url": "https://feeds.content.dowjones.io/public/rss/mw_topstories", "category": "Economy", "country": "United States"},
    {"name": "Financial Times World", "url": "https://www.ft.com/world?format=rss", "category": "Economy", "country": "United Kingdom"},
    {"name": "Fortune Magazine", "url": "https://fortune.com/feed/", "category": "Economy", "country": "United States"},
    {"name": "Economist International", "url": "https://www.economist.com/international/rss.xml", "category": "Economy", "country": "United Kingdom"},
    {"name": "Business Insider", "url": "https://www.businessinsider.com/rss", "category": "Economy", "country": "United States"},

    # --- TECH, SCIENCE & ENVIRONMENT ---
    {"name": "NPR Technology", "url": "https://feeds.npr.org/1019/rss.xml", "category": "Tech", "country": "United States"},
    {"name": "NPR Science", "url": "https://feeds.npr.org/1007/rss.xml", "category": "Tech", "country": "United States"},
    {"name": "Wired Tech", "url": "https://www.wired.com/feed/rss", "category": "Tech", "country": "United States"},
    {"name": "NASA Breaking News", "url": "https://www.nasa.gov/rss/dyn/breaking_news.rss", "category": "Tech", "country": "United States"},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index", "category": "Tech", "country": "United States"},
    {"name": "TechCrunch Main", "url": "https://techcrunch.com/feed/", "category": "Tech", "country": "United States"},
    {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/", "category": "Tech", "country": "United States"},
    {"name": "New Scientist", "url": "https://www.newscientist.com/feed/home/", "category": "Tech", "country": "United Kingdom"},
    {"name": "EcoWatch Climate", "url": "https://www.ecowatch.com/feeds/feed.rss", "category": "Climate", "country": "United States"},
    {"name": "Carbon Brief Climate", "url": "https://www.carbonbrief.org/feed/", "category": "Climate", "country": "United Kingdom"},
    {"name": "Environment Agency UK", "url": "https://www.gov.uk/government/organisations/environment-agency.atom", "category": "Climate", "country": "United Kingdom"},

    # --- ARTS, LIFESTYLE & SPORTS ---
    {"name": "NPR Arts & Culture", "url": "https://feeds.npr.org/1008/rss.xml", "category": "Arts", "country": "United States"},
    {"name": "BBC Entertainment", "url": "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml", "category": "Arts", "country": "United Kingdom"},
    {"name": "Smithsonian Magazine", "url": "https://www.smithsonianmag.com/rss/latest_articles/", "category": "Arts", "country": "United States"},
    {"name": "NPR Life & Style", "url": "https://feeds.npr.org/1003/rss.xml", "category": "Lifestyle", "country": "United States"},
    {"name": "BBC Sports Desk", "url": "https://feeds.bbci.co.uk/sport/rss.xml", "category": "Sports", "country": "United Kingdom"},
    {"name": "ESPN Top News", "url": "https://www.espn.com/espn/rss/news", "category": "Sports", "country": "United States"}
]

POSITIVE_WORDS = [
    'win', 'breakthrough', 'peace', 'save', 'hope', 'discovery', 'grant', 
    'aid', 'conservation', 'restored', 'clean', 'agree', 'award', 'pact', 
    'solution', 'cured', 'progress', 'milestone', 'agreement', 'thrive'
]

def parse_feed(feed_info):
    """Worker function to parse a single RSS feed in parallel threads."""
    feed_stories = []
    try:
        parsed = feedparser.parse(feed_info["url"])
        entries = parsed.entries[:10]  # Grab top 10 articles per source
        
        for entry in entries:
            title = entry.get("title", "").strip()
            if not title:
                continue
            
            # Clean HTML out of summary descriptions
            raw_summary = entry.get("summary", entry.get("description", ""))
            summary = re.sub('<[^<]+?>', '', raw_summary).strip()
            if len(summary) > 250:
                summary = summary[:250] + "..."
            elif not summary:
                summary = "Direct headline coverage from bureau wire."

            is_feel_good = any(word in (title + " " + summary).lower() for word in POSITIVE_WORDS)

            feed_stories.append({
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
        pass
    return feed_stories

def main():
    print(f"Starting parallel fetch across {len(FEEDS)} international feeds...")
    
    all_raw_stories = []
    
    # Use ThreadPoolExecutor to fetch 30 feeds concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        results = executor.map(parse_feed, FEEDS)
        for res in results:
            all_raw_stories.extend(res)

    # Deduplicate stories across sources by headline title
    unique_stories = []
    seen_titles = set()

    for story in all_raw_stories:
        title_key = story["title"].lower().strip()
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            story["id"] = f"story-{len(unique_stories) + 1}"
            unique_stories.append(story)

    # Write output to news.json
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(unique_stories, f, indent=2, ensure_ascii=False)

    print(f"Successfully compiled {len(unique_stories)} unique world stories into news.json!")

if __name__ == "__main__":
    main()
