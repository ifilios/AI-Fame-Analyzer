import requests
import json
import time
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from pytrends.request import TrendReq

load_dotenv()


def get_celebrity_info_and_views(name):
    """
    Επιστρέφει μόνο τα απαραίτητα στοιχεία για έναν celebrity από την Wikipedia:
    - extract (summary)
    - pageviews (τελευταίες 60 ημέρες)
    - κύρια εικόνα
    - URL σελίδας
    """
    base_url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts|pageviews|pageimages|info",
        "exintro": True,
        "explaintext": True,
        "inprop": "url",
        "piprop": "original",
        "titles": name
    }

    headers = {
        'User-Agent': 'MyLearningBot/1.0 (myemail@example.com)'
    }

    try:
        response = requests.get(base_url, params=params, headers=headers)
        if response.status_code != 200:
            return {"error": f"Σφάλμα API: {response.status_code}"}

        data = response.json()
        pages = data.get("query", {}).get("pages", {})

        for page_id, page_info in pages.items():
            if page_id == "-1":
                return {"error": f"Δεν βρέθηκε σελίδα για: {name}"}

            extract = page_info.get("extract", "Δεν βρέθηκε κείμενο.")
            views_dict = page_info.get("pageviews", {})
            total_views = sum(views for views in views_dict.values() if views is not None)
            image_url = page_info.get("original", {}).get("source")
            page_url = page_info.get("fullurl")

            result = {
                "name": name,
                "extract": extract,
                "pageviews_last_60_days": total_views,
                "image_url": image_url,
                "page_url": page_url
            }

            # Τύπωμα στο terminal, καθε στοιχείο σε ξεχωριστή γραμμή
            print(json.dumps(result, indent=4, ensure_ascii=False))

            return result

    except requests.exceptions.RequestException as e:
        return {"error": f"Αποτυχία σύνδεσης: {e}"}


import time

import json
import requests
import os


def get_data_with_serper(real_name):
    print(f"\n--- Αναζήτηση για: {real_name} ---")

    search_url = "https://google.serper.dev/search"
    payload = json.dumps({"q": f"{real_name} official instagram site:instagram.com"})
    headers = {
        'X-API-KEY': os.getenv("SERPER_API_KEY"),
        'Content-Type': 'application/json'
    }

    username = None
    try:
        response = requests.post(search_url, headers=headers, data=payload)
        results = response.json()

        for result in results.get('organic', []):
            link = result.get('link', '')
            if "instagram.com/" in link and all(x not in link for x in ["/p/", "/reel/", "/explore/"]):
                username = link.strip('/').split('/')[-1].split('?')[0]
                break
    except Exception as e:
        print(f"[DEBUG] Σφάλμα στο Serper: {e}")
        return {"error": f"Σφάλμα στο Serper: {e}", "followers": 0}

    if not username:
        print(f"[DEBUG] Δεν βρέθηκε username για το ερώτημα: {real_name}")
        return {"error": f"Δεν βρέθηκε προφίλ για τον/την {real_name}.", "followers": 0}

    print(f"[DEBUG] Βρέθηκε το username: @{username}. Στέλνω αίτημα στο RapidAPI...")

    api_url = "https://instagram-statistics-api.p.rapidapi.com/community"
    profile_url = f"https://www.instagram.com/{username}/"
    rapid_headers = {
        "x-rapidapi-host": "instagram-statistics-api.p.rapidapi.com",
        "x-rapidapi-key": os.getenv("RAPID_API_KEY")
    }

    try:
        res = requests.get(api_url, headers=rapid_headers, params={"url": profile_url})
        if res.status_code == 200:
            data = res.json()
            inner_data = data.get("data", {})
            followers = inner_data.get("usersCount") or inner_data.get("followers") or inner_data.get("follower_count")

            if followers:
                num_followers = int(followers)
                formatted = f"{num_followers:,}".replace(",", ".")
                # Επιστρέφουμε dictionary με το κείμενο ΚΑΙ τον καθαρό αριθμό
                return {
                    "description": f"ΑΠΟΤΕΛΕΣΜΑ: {real_name} -> @{username} -> {formatted} followers.",
                    "followers": num_followers,
                    "username": username
                }
            else:
                return {"error": "Δεν βρέθηκε αριθμός followers", "followers": 0}
        else:
            return {"error": f"Σφάλμα RapidAPI (Status {res.status_code})", "followers": 0}

    except Exception as e:
        return {"error": str(e), "followers": 0}


def get_news_mentions(celebrity_name, days=28):
    API_KEY = os.getenv("NEWS_KEY")

    # 1. Υπολογισμός ημερομηνιών
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": celebrity_name,
        "language": "en",
        "sortBy": "publishedAt",
        "from": start_date.strftime("%Y-%m-%d"),
        "to": end_date.strftime("%Y-%m-%d"),
        "pageSize": 50,
        "apiKey": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") != "ok":
        print("Error:", data.get("message"))
        # Επιστρέφουμε JSON string για το σφάλμα
        return json.dumps({"total_mentions": 0, "top_articles": []})

    # 2. Παίρνουμε τον ΠΡΑΓΜΑΤΙΚΟ αριθμό από το API (όχι το len της λίστας)
    true_total_mentions = data.get("totalResults", 0)

    articles = data.get("articles", [])
    top_articles = [{"title": a["title"], "source": a["source"]["name"], "url": a["url"]}
                    for a in articles[:5]]

    # Επιστρέφουμε JSON string για τα επιτυχημένα αποτελέσματα
    return json.dumps({
        "total_mentions": true_total_mentions,
        "top_articles": top_articles
    })


def get_youtube_stats(celebrity_name):
    load_dotenv()

    search_url = "https://www.googleapis.com/youtube/v3/search"
    search_params = {
        "part": "snippet",
        "q": celebrity_name,
        "type": "channel",
        "maxResults": 1,
        "key": os.getenv("YT_KEY")
    }

    try:
        search_response = requests.get(search_url, params=search_params)
        search_data = search_response.json()

        if "error" in search_data:
            print(f"YouTube API Error: {search_data['error']['message']}")
            return None

        if not search_data.get("items"):
            print("No channel found for this name.")
            return None

        if not search_data.get("items"):
            return None

        channel_id = search_data["items"][0]["snippet"]["channelId"]
        channel_title = search_data["items"][0]["snippet"]["title"]

        stats_url = "https://www.googleapis.com/youtube/v3/channels"
        stats_params = {
            "part": "statistics",
            "id": channel_id,
            "key": os.getenv("YT_KEY")
        }

        stats_response = requests.get(stats_url, params=stats_params)
        stats_data = stats_response.json()

        if stats_data.get("items"):
            stats = stats_data["items"][0]["statistics"]
            return {
                "youtube_channel": channel_title,
                "youtube_subscribers": int(stats.get("subscriberCount", 0)),
                "youtube_videos": int(stats.get("videoCount", 0)),
                "youtube_total_views": int(stats.get("viewCount", 0))
            }

    except Exception as e:
        print(f"⚠️ Σφάλμα: {e}")
        return None


def get_google_trends_stats(celebrity_name):

    my_proxies = []

    pytrends = TrendReq(hl='en-US', tz=360, proxies=my_proxies)

    try:

        time.sleep(5)

        kw_list = [celebrity_name]
        pytrends.build_payload(kw_list, cat=0, timeframe='today 1-m', geo='', gprop='')

        data = pytrends.interest_over_time()
        avg_score = float(round(data[celebrity_name].mean(), 2)) if not data.empty else 0

        related = pytrends.related_queries()
        top_queries = []
        if related[celebrity_name]['top'] is not None:
            top_queries = related[celebrity_name]['top']['query'].head(3).tolist()

        regions = pytrends.interest_by_region(resolution='COUNTRY', inc_low_vol=True, inc_geo_code=False)
        top_regions = regions.sort_values(by=celebrity_name, ascending=False).head(3).index.tolist()

        return {
            "trends_score": avg_score,
            "trending_topics": top_queries,
            "top_countries": top_regions,
            "status": "Success"
        }

    except Exception as e:
        if "429" in str(e):
            return {"error": "Google Trends rate limit. Wait a bit longer."}
        return {"error": str(e)}
