from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from openai import OpenAI
import os
from pydantic import BaseModel
from ai_extractor import extract_name, extract_metric, final_answer
from crawlers import get_celebrity_info_and_views, get_data_with_serper, get_news_mentions, get_youtube_stats, get_google_trends_stats
import json
import math

app = FastAPI()

# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory=os.getcwd()), name="static")

# Serve index.html at /
@app.get("/")
def serve_index():
    return FileResponse("index.html")

origins = [
    "http://localhost:63342",
    "http://127.0.0.1:63342"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PromptRequest(BaseModel):
    prompt: str


@app.post("/callAI")
def openAI_router(request: PromptRequest):
    load_dotenv()

    client = OpenAI(
        api_key=os.getenv("OPEN_AI_KEY")
    )

    question = request.prompt

    try:

        # Extract name
        name = extract_name(question)  # ai extractor name
        metrics = extract_metric(question)  # ai returns a string with the metrics required on the input

        requested_metrics = [metric.strip() for metric in metrics.split(',')]

        # None metric is found at first
        wiki_info = None
        insta_followers = None
        news_mentions = None
        yt_stats = None
        google_trends = None
        fame_score = None

        requested_metrics = set(requested_metrics)
        if "fame_score" in requested_metrics:
            # Η update λειτουργεί τέλεια σε sets
            requested_metrics.update([
                "instagram_followers",
                "wiki_views",
                "news_mentions",
                "youtube_stats"
            ])

        # Checking which metric exists in requested_metrics
        if "wiki_views" in requested_metrics:
            wiki_info = get_celebrity_info_and_views(name)

        if "instagram_followers" in requested_metrics:
            insta_followers = get_data_with_serper(name)

        if "news_mentions" in requested_metrics:
            news_mentions = get_news_mentions(name)

        if "youtube_stats" in requested_metrics:
            yt_stats = get_youtube_stats(name)

        if "google_trends" in requested_metrics:
            google_trends = get_google_trends_stats(name)

        if "fame_score" in requested_metrics:
            # 1. Wiki: Από το dictionary 'wiki_info' απομονώνουμε τον αριθμό
            raw_wiki_count = wiki_info.get("pageviews_last_60_days", 0)

            # 2. News: Μετατρέπουμε το JSON string 'news_mentions' σε dict και παίρνουμε τον αριθμό
            news_dict = json.loads(news_mentions)
            raw_news_count = news_dict.get("total_mentions", 0)

            # 3. YouTube: Από το dict 'yt_stats' παίρνουμε τους subscribers
            raw_yt_subs = yt_stats.get("youtube_subscribers", 0)

            raw_insta_followers = insta_followers.get("followers", 0)

            fame_score = getFameScore(
                int(raw_insta_followers),
                int(raw_yt_subs),
                int(raw_wiki_count),
                int(raw_news_count)
            )

        if "NONE" in requested_metrics:
            print("No valid metrics requested.")

        crawled_data = {
            "wiki_info": wiki_info,
            "instagram_followers": insta_followers,
            "news_mentions": news_mentions,
            "yt_stats": yt_stats,
            "google_trends": google_trends,
            "fame_score": fame_score
        }
        # RAG answer
        answer = final_answer(crawled_data, question)

        return {"answer": answer}

    except Exception as e:
        print(f"❌ Σφάλμα API: {e}")
        return {"answer": "A technical issue occurred. Please try again later."}


def getFameScore(insta_followers, yt_subs, wiki_views_60d, news_count_30d):
    # Μετατροπή σε float για ασφάλεια
    insta = float(insta_followers or 0)
    yt = float(yt_subs or 0)
    wiki = float(wiki_views_60d or 0)
    news = float(news_count_30d or 0)

    # 1. Logarithmic Scoring (Αποφεύγει το απότομο 1.0 limit)
    # Χρησιμοποιούμε log10 για να δίνουμε αξία στα τεράστια νούμερα
    # Insta: 100M -> ~1.0, 600M -> ~1.1
    s_insta = math.log10(insta + 1) / 8.0
    s_yt = math.log10(yt + 1) / 7.0
    s_wiki = math.log10(wiki + 1) / 6.3
    s_news = math.log10(news + 1) / 3.0

    # Περιορισμός max (για να μην ξεφύγει πάνω από 1.2 π.χ. σε ακραίες περιπτώσεις)
    s_insta = min(s_insta, 1.15)
    s_yt = min(s_yt, 1.15)
    s_wiki = min(s_wiki, 1.15)
    s_news = min(s_news, 1.15)

    # 2. Dynamic Weighting (Αν λείπει το YouTube, μην τον θάβεις)
    if yt < 50000:
        # Ανακατανομή: Insta 50%, Wiki 30%, News 15%, YT 5%
        w_insta, w_yt, w_wiki, w_news = 0.50, 0.05, 0.30, 0.15
    else:
        # Standard: Insta 40%, YT 25%, Wiki 20%, News 15%
        w_insta, w_yt, w_wiki, w_news = 0.40, 0.25, 0.20, 0.15

    final_score = (s_insta * w_insta) + (s_yt * w_yt) + (s_wiki * w_wiki) + (s_news * w_news)

    # 3. Final Multiplier & Rounding
    total_points = round(final_score * 100, 1)

    # "Hard Ceiling" στα 100
    total_points = min(total_points, 100.0)

    # Fame Level Logic
    if total_points >= 88:
        label, desc = "Legend", "A global icon dominating all platforms and generations."
    elif total_points >= 65:
        label, desc = "Superstar", "Huge mainstream appeal and massive digital footprint."
    elif total_points >= 40:
        label, desc = "A-Lister", "Major industry player with consistent relevance."
    elif total_points >= 15:
        label, desc = "Rising Star", "Building significant momentum in their field."
    else:
        label, desc = "Niche / Local", "Recognized in specific circles or regional markets."

    return {
        "score": total_points,
        "level": label,
        "description": desc
    }
